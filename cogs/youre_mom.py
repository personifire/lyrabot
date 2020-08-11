import bisect
import random
import re

from discord.ext import commands
import spacy
from spacy.util import compile_prefix_regex, compile_suffix_regex


def ym_dep(tokens):
    """Yield "you're mom" substitutions by analyzing the dependencies of tokens.

    Each substitution is a list of replacements. Each replacement is a tuple of
    ((start_char, end_char), string).
    """
    for token in tokens:
        parent = token.head
        grandparent = parent.head
        if token.dep_ == "poss" and token.tag_ != "WP$":
            yield [(subtree_bounds(token), "you're mom's")]
        elif (
            token.dep_ in ["dobj", "attr", "pobj"]
            or (token.dep_ == "pcomp" and token.lower_ != "of")
            or (token.dep_ == "dative" and token.tag_ != "IN")
            or (token.dep_ == "oprd" and token.pos_ in ["NOUN", "PROPN"])
        ) and not (
            # Ensure there is no wh-movement
            token.i < parent.i
            or (
                token.dep_ == "pobj"
                and token.tag_ in ["WP", "WDT"]
                and parent.i < grandparent.i
            )
        ):
            yield [(subtree_bounds(token), "you're mom")]
        elif token.dep_ in ["nsubj", "nsubjpass", "csubj", "csubjpass"] and not (
            parent.dep_ in ["relcl", "csubj", "csubjpass"]
            and token.left_edge.tag_ in ["WP", "WDT", "WP$"]
        ):
            # Insert extra space when replacing the "us" in "Let's"
            lets_ws = token.lower_ in ["s", "'s", "’s"] and not token.nbor(-1).whitespace_
            sub = [(subtree_bounds(token), (" " * lets_ws) + "you're mom")]

            verb = try_verb(parent)
            if verb:
                sub.append(verb)
            yield sub


def ym_sentence(sent):
    """Return a "you're mom" substitution for the given sentence span.

    A substitution is a list of replacements. Each replacement is a tuple of
    ((start_char, end_char), string). If no replacements can be made, an empty
    list is returned.
    """
    sub = []
    sub_ranges = []
    # Equation found through testing and regression
    sub_target = max(1, round(len(sent) / 25 + 0.5))
    tokens = list(sent)
    # Shuffle tokens to keep things interesting
    random.shuffle(tokens)
    for dep_sub in ym_dep(tokens):
        start = min(s[0][0] for s in dep_sub)
        end = max(s[0][1] for s in dep_sub)
        i = bisect.bisect_left(sub_ranges, (start, end))
        if (i == 0 or sub_ranges[i - 1][1] <= start) and (
            i == len(sub_ranges) or end <= sub_ranges[i][0]
        ):
            sub.extend(dep_sub)
            sub_ranges.insert(i, (start, end))

            sub_target -= 1
            if sub_target == 0:
                break

    if len(sub) > 0:
        return sub

    for token in tokens:
        if token.pos_ in ["NOUN", "PROPN", "PRON"]:
            return [(token_bounds(token), "you're mom")]

    if sent.root.pos_ not in ["PUNCT", "SYM", "X"]:
        return [(token_bounds(sent.root), "you're mom")]

    return []


def token_bounds(token):
    return (token.idx, token.idx + len(token))


def subtree_bounds(token):
    # Try to preserve as much whitespace and punctuation as possible
    left = token.left_edge
    while left.i < token.i and (left.is_punct or left.is_space):
        left = left.nbor(1)
    right = token.right_edge
    while token.i < right.i and (right.is_punct or right.is_space):
        right = right.nbor(-1)
    return (left.idx, right.idx + len(right))


SPECIAL_VERBS = {
    "am"   : "is",
    "are"  : "is",
    "were" : "was",
    "have" : "has",
    "do"   : "does",
    "'m"   : "'s",
    "'re"  : "'s",
    "'ve"  : "'s",
    "’m"   : "’s",
    "’re"  : "’s",
    "’ve"  : "’s",
    "m"    : "s",
    "re"   : "s",
    "ve"   : "s",
}
VERB_IES = re.compile("[^aeiou]y$", re.IGNORECASE)
VERB_ES = re.compile("(s|x|z|[cs]h|[^aeiou]o)$", re.IGNORECASE)


def try_special_verb(token):
    if token.lower_ in SPECIAL_VERBS:
        repl = SPECIAL_VERBS[token.lower_]
        # Try to match the capitalization of the verb.
        if token.text[0].isupper():
            repl = repl.title()
        return (token_bounds(token), repl)


def try_verb(token):
    # VB, VBG, and VBN are similar enough to handle together
    if token.tag_ in ["VB", "VBG", "VBN"] and not any(
        map(lambda c: c.tag_ == "MD", token.children)
    ):
        for child in filter(lambda c: c.dep_ in ["aux", "auxpass"], token.children):
            verb = try_special_verb(child)
            if verb:
                return verb
    elif token.tag_ == "VBD":
        return try_special_verb(token)
    elif token.tag_ == "VBP" and token.lower_ != "ai":
        verb = try_special_verb(token)
        if verb is None:
            end = token.idx + len(token)
            if VERB_IES.search(token.text):
                return ((end - 1, end), "ies")
            elif VERB_ES.search(token.text):
                return ((end, end), "es")
            else:
                return ((end, end), "s")
        else:
            return verb


class youre_mom(commands.Cog):
    def __init__(self):
        # Disable named entity recognition for performance
        self.nlp = spacy.load("en_core_web_sm", disable=["ner"])
        setup_nlp_markup(self.nlp)

    @commands.command(aliases=["ym"])
    async def youremom(self, ctx, *, text):
        """ you're mom """
        doc = self.nlp(text)
        ym_text = ""
        i = 0
        for sent in doc.sents:
            for (start, end), repl in sorted(ym_sentence(sent)):
                ym_text += text[i:start] + repl
                i = end
            if len(ym_text) >= 2000:
                break

        ym_text += text[i:]
        if text == ym_text:
            # If no substitutions were found, return "you're mom" instead of
            # repeating the user's message
            await ctx.send("you're mom")
        else:
            await ctx.send(ym_text[:2000])


def setup(client):
    client.add_cog(YoureMom())


MENTION_EMOJI = re.compile(r"<(#|@[!&]?|a?:[A-Za-z0-9_]{2,}:)\d+>")

def retokenize_mention_emoji(doc):
    with doc.retokenize() as retokenizer:
        for match in MENTION_EMOJI.finditer(doc.text):
            start, end = match.span()
            span = doc.char_span(start, end)
            if span is not None:
                retokenizer.merge(span)
    return doc


def setup_nlp_markup(nlp):
    prefixes = nlp.Defaults.prefixes + ("~", "\\|\\|")
    suffixes = nlp.Defaults.suffixes + ("~", "\\|\\|")
    nlp.tokenizer.prefix_search = compile_prefix_regex(prefixes).search
    nlp.tokenizer.suffix_search = compile_suffix_regex(suffixes).search
    nlp.add_pipe(retokenize_mention_emoji, first=True)
