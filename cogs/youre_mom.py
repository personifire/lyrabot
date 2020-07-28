import random
import re

from discord.ext import commands
import spacy
from spacy.util import compile_prefix_regex, compile_suffix_regex


def ym_sentence(sent):
    """Given a sentence, return a "you're mom" substitution.

    Args:
        sent (Span): The sentence to process. Usually from `Doc.sents`.

    Returns:
        A list of replacements. Each replacement is a tuple of
        ((start_char, end_char), replacement). If no replacements can be made,
        an empty list is returned.
    """
    # Shuffle tokens to keep things interesting
    tokens = list(sent)
    random.shuffle(tokens)
    for token in tokens:
        parent = token.head
        grandparent = parent.head
        if token.dep_ == "poss" and token.tag_ != "WP$":
            return [(subtree_bounds(token), "you're mom's")]
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
            return [(subtree_bounds(token), "you're mom")]
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
            return sub
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


class YoureMom(commands.Cog):
    def __init__(self):
        # Disable named entity recognition for performance
        self.nlp = spacy.load("en_core_web_sm", disable=["ner"])
        setup_nlp_markup(self.nlp)

    @commands.command()
    async def ym(self, ctx, *, text):
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
