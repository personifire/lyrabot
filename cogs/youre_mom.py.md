# you're mom

*(Note: This is a [literate program](https://en.wikipedia.org/wiki/Literate_programming). To turn it into a runnable program, use the [lit](https://github.com/vijithassar/lit) preprocessor.)*

<!-- For the explacy diagrams, we have to use fenced code blocks with the `text` language. If we use indented code blocks, GitHub will apply Python syntax highlighting. But, lit doesn't support ignoring code blocks by language. To get around this, we indent every `text` code block by at least one space. This doesn't change how the Markdown renders, but it does ensure that lit's /^```/ regex will ignore the blocks. -->

**you're mom** is a type of [maternal insult](https://en.wikipedia.org/wiki/Maternal_insult). It is used in many ways, but the most common is the *substitution*. In this form, the insult is created by repeating what someone says but with part of their sentence replaced with "you're mom":

> A: "What is the purpose of **this**?"
>
> B: "What is the purpose of **you're mom**?"

In this article, we write a [discord.py](https://discordpy.readthedocs.io/) cog to produce "you're mom" substitutions.

## Contents

* [Resources](#resources)
* [Theory](#theory)
* [Implementation](#implementation)
  * [Imports](#imports)
  * [`ym_dep`](#ym_dep)
    * [Possession modifier](#possession-modifier)
    * [Objects](#objects)
    * [Subjects](#subjects)
    * [Excluded dependencies](#excluded-dependencies)
  * [`ym_sentence`](#ym_sentence)
  * [Helpers](#helpers)
  * [Verbs](#verbs)
  * [discord.py cog](#discordpy-cog)
  * [Discord message formatting](#discord-message-formatting)
* [Future work](#future-work)

## Resources

In this article, we frequently reference part-of-speech tags and dependency labels. These tags and labels have cryptic names, so here are guides explaining what the names mean:

* [spaCy English part-of-speech tags](https://spacy.io/api/annotation/#pos-en)
* [ClearNLP dependency labels](https://github.com/clir/clearnlp-guidelines/blob/master/md/specifications/dependency_labels.md)

If you want to visualize a processed sentence, a helpful tool is [explacy](https://github.com/tylerneylon/explacy). (Note that there's [a bug](https://github.com/tylerneylon/explacy/issues/3)—use [this fork](https://github.com/bionandojr/explacy) for the unmerged fix.)

## Theory

To produce substitutions, we must first understand what "you're mom" is. Grammatically, "you're mom" is a [noun phrase](https://en.wikipedia.org/wiki/Noun_phrase). Noun phrases can [function](https://en.wikipedia.org/wiki/Grammatical_relation) as many things: [subjects](https://en.wikipedia.org/wiki/Subject_(grammar)), [objects](https://en.wikipedia.org/wiki/Object_(grammar)), etc. We will call these syntactic roles *dependencies*. For example, here is a sentence with its dependencies:

 ```text
 Dep tree Token Dep type
 ──────── ───── ────────
    ┌─►   He    nsubj
 ┌──┴──   boops ROOT
 │  ┌─►   the   det
 └─►└──   snout dobj
 ```

The first column shows the directed edges of the dependency tree. The second column shows the tokens of the sentence. The third column shows the type of dependency. "He" is the subject of the sentence, so it is marked as a nominal subject (`nsubj`). "boops" is the verb and is marked as the `ROOT` by convention. "the snout" is a direct object (`dobj`), as "He" is booping "the snout". Finally, "the" is a [determiner](https://en.wikipedia.org/wiki/English_determiners) (`det`). Specifically, it is the determiner for "snout", which we can see from the directed edge from "snout" to "the".

How does this help us produce substitutions? As a noun phrase, "you're mom" can function as (almost) anything that any noun phrase can function as. For example, a noun phrase can be a `nsubj`. This means that "you're mom" can replace (almost) any `nsubj`. If we replace the `nsubj` in this example, we get "**you're mom** boops the snout", which makes sense. As another example, a noun phrase cannot be a `det`. If we try to replace the `det`, we get "He boops **you're mom** snout", which makes no sense.

This suggests a strategy:
* Figure out every type of dependency that "you're mom" can replace.
* For a given sentence, identify the dependency of each token.
* Pick a random token which has a valid dependency and replace it with "you're mom".

## Implementation

To perform natural language processing, we use [spaCy](https://spacy.io/) and the [`en_core_web_sm`](https://spacy.io/models/en#en_core_web_sm) model. For Discord bot integration, we use [discord.py](http://discordpy.rtfd.org/).

The program itself has two main parts:

1. `ym_sentence`, `ym_dep`: Analyze a sentence and return a "you're mom" substitution.
2. discord.py cog: Take a chat message, pass each sentence to `ym_sentence`, and return the output.

Disclaimer: English is complicated and the model isn't perfect. We try to keep things simple and cover the common cases. Anything more is too much, especially for a literate program.

### Imports

```python
import bisect
import random
import re

from discord.ext import commands
import spacy
from spacy.util import compile_prefix_regex, compile_suffix_regex
```

### `ym_dep`

```python
def ym_dep(tokens):
    """Yield "you're mom" substitutions by analyzing the dependencies of tokens.

    Each substitution is a list of replacements. Each replacement is a tuple of
    ((start_char, end_char), string).
    """
    for token in tokens:
        parent = token.head
        grandparent = parent.head
```

#### Possession modifier

```python
        if token.dep_ == "poss" and token.tag_ != "WP$":
            yield [(subtree_bounds(token), "you're mom's")]
```

<details>
<summary>Why do we exclude <code>WP$</code>?</summary>

The `poss` label applies to three categories:

1. Possessive determiners (`PRP$`): e.g. "**My** car is parked."
2. Nouns with *'s* suffix: e.g. "**John's** car is parked."
3. The word "whose" (`WP$`): e.g. "**Whose** car is parked?"

We exclude `WP$` because, unlike the other categories, "whose" cannot always be replaced by "you're mom's". The above example works ("**you're mom's** car is parked?"), but these do not:

> A: "**Whose** car are you talking about?"
>
> B: "**you're mom's** car are you talking about?"

> A: "Find the person **whose** car is parked."
>
> B: "Find the person **you're mom's** car is parked."

It's too much effort to handle these cases, so we just exclude `WP$`.

---
</details>

#### Objects

```python
        elif (
            token.dep_ in ["dobj", "attr", "pobj"]
            or (token.dep_ == "pcomp" and token.lower_ != "of")
            or (token.dep_ == "dative" and token.tag_ != "IN")
            or (token.dep_ == "oprd" and token.pos_ in ["NOUN", "PROPN"])
```
<details>
<summary>Why does <code>pcomp</code> need an extra check?</summary>

`pcomp` stands for "complement of a preposition". In sentences that use "because of" or "instead of", the "of" is marked as a `pcomp`. But, it doesn't make sense to replace "of". For example:

 ```text
 Dep tree Token   Dep type Tag Part of Sp
 ──────── ─────── ──────── ─── ──────────
 ┌─►┌┬──  Because prep     IN  SCONJ
 │  │└─►  of      pcomp    IN  ADP
 │  └──►  you     pobj     PRP PRON
 │ ┌───►  ,       punct    ,   PUNCT
 │ │┌──►  I       nsubj    PRP PRON
 │ ││┌─►  never   neg      RB  ADV
 └─┴┴┴──  stray   ROOT     VBP VERB
 ```

Replacing "of" gives us "Because **you're mom** you, I never stray", which doesn't make sense. So, we need a check.

---
</details>

<details>
<summary>Why does <code>dative</code> need an extra check?</summary>

A dative is the object of a [dative-shifting verb](https://en.wikipedia.org/wiki/Dative_shift). Basically, an indirect object. We can only replace it when `dative` marks a noun:

 ```text
 Dep tree Token Dep type Tag Part of Sp
 ──────── ───── ──────── ─── ──────────
 ┌┬──     Give  ROOT     VB  VERB
 │└─►     me    dative   PRP PRON
 └──►     it    dobj     PRP PRON
 ```

And not when `dative` marks a preposition (which is always "to" or "for"):

 ```text
 Dep tree Token Dep type Tag Part of Sp
 ──────── ───── ──────── ─── ──────────
 ┌──┬──   Give  ROOT     VB  VERB
 │  └─►   it    dobj     PRP PRON
 └─►┌──   to    dative   IN  ADP
    └─►   me    pobj     PRP PRON
 ```

In the first example, substituting produces "Give **you're mom** it", which makes sense. Substituting in the second example produces "Give it **you're mom**". While that makes sense, the preposition "to" has been deleted. Instead, we let `pobj` cover this case, as it will correctly produce "Give it to **you're mom**".

---
</details>

<details>
<summary>Why does <code>oprd</code> need an extra check?</summary>

`oprd` stands for "object predicate". Unfortunately, I can't find any information on "object predicates", so all I know is that the ClearNLP spec says that it's a type of object. But, sometimes `oprd` is noun-like:

* "They elected him **president**."
* "They called her **a thief**."
* "Keep my identity **a secret**."

And sometimes, it is not:

* "It seems **safe**."
* "When will it be made **available**?"

So, we only replace `oprd` when it is a noun or proper noun.

---
</details>

```python
        ) and not (
            # Ensure there is no wh-movement
            token.i < parent.i
            or (
                token.dep_ == "pobj"
                and token.tag_ in ["WP", "WDT"]
                and parent.i < grandparent.i
            )
        ):
```

<details>
<summary>What is wh-movement?</summary>

[Wh-movement](https://en.wikipedia.org/wiki/Wh-movement) is the difference in word order between normal sentences and question sentences. It's called "wh-movement" because it happens with wh-words, such as **wh**o, **wh**om, **wh**ose, **wh**at, **wh**ich, etc. For example:

> Q: "**What** do you like?"
>
> A: "I like **nothing**."

In the answer, the object is in its canonical position after the verb. But, in the question, the object is at the front of the sentence. The problem is that "you're mom" substitutions don't work when the object is in the question position:

> "**you're mom** do you like?" (doesn't work)
>
> "I like **you're mom**." (works)

So, we can't substitute the object when there is wh-movement. (Actually, the substitution kind of works when there's [pied-piping](https://en.wikipedia.org/wiki/Wh-movement#Pied-piping), but it turned out to be too annoying to implement.)

---
</details>

<details>
<summary>How do we detect wh-movement?</summary>

Usually, we can detect wh-movement by checking if the object is before its parent. (This parent is a preposition for `pobj` and `pcomp` and a verb for the other objects.) For `pobj`, though, if the preposition is not [stranded](https://en.wikipedia.org/wiki/Preposition_stranding), then the `pobj` will not be before its parent `prep`, but there may still be wh-movement. For example:

 ```text
 Dep tree     Token  Dep type Tag Part of Sp
 ──────────── ────── ──────── ─── ──────────
 ┌─────────── Find   ROOT     VB  VERB
 │        ┌─► the    det      DT  DET
 └─►┌─────┴── person dobj     NN  NOUN
    │  ┌─►┌── to     prep     IN  ADP
    │  │  └─► whom   pobj     WP  PRON
    │  │  ┌─► I      nsubj    PRP PRON
    └─►└──┴── spoke  relcl    VBD VERB
 ```

Substituting the `pobj` here would produce "Find the person to **you're mom** I spoke", which doesn't make sense. So, we have an extra check to catch these kinds of situations.

---
</details>

```python
            yield [(subtree_bounds(token), "you're mom")]
```

#### Subjects

```python
        elif token.dep_ in ["nsubj", "nsubjpass", "csubj", "csubjpass"] and not (
            parent.dep_ in ["relcl", "csubj", "csubjpass"]
            and token.left_edge.tag_ in ["WP", "WDT", "WP$"]
        ):
```

<details>
<summary>What is the <code>and not (...)</code> check for?</summary>

If the subject is a [relative pronoun](https://en.wikipedia.org/wiki/Relative_pronoun) that belongs to a [relative clause](https://en.wikipedia.org/wiki/English_relative_clauses), then we can't replace it. For example:

 ```text
 Dep tree  Token Dep type Tag Part of Sp
 ───────── ───── ──────── ─── ──────────
 ┌──────── Find  ROOT     VB  VERB
 │     ┌─► the   det      DT  DET
 └─►┌──┴── one   dobj     NN  NOUN
    │  ┌─► who   nsubj    WP  PRON
    └─►├── did   relcl    VBD AUX
       └─► it    dobj     PRP PRON
 ```

If we try to replace the `nsubj`, we get "Find the one **you're mom** did it", which doesn't make sense.

The same applies to *-ever* pronouns in `csubj` and `csubjpass`:

 ```text
 Dep tree Token   Dep type Tag Part of Sp
 ──────── ─────── ──────── ─── ──────────
    ┌──►  Whoever nsubj    WP  PRON
    │┌─►  is      aux      VBZ AUX
 ┌─►└┴──  hiding  csubj    VBG VERB
 │   ┌─►  can     aux      MD  VERB
 └───┼──  come    ROOT     VB  VERB
     └─►  out     prt      RP  ADP
 ```

If we replace "Whoever", we get "**you're mom** is hiding can come out", which doesn't make sense.

Finally, we use `.left_edge` to catch cases of "whose [noun]":

 ```text
 Dep tree  Token    Dep type Tag Part of Sp
 ───────── ──────── ──────── ─── ──────────
       ┌─► The      det      DT  DET
 ┌─────┴── one      ROOT     NN  NOUN
 │     ┌─► whose    poss     WP$ DET
 │  ┌─►└── umbrella nsubj    NN  NOUN
 └─►└──┬── did      relcl    VBD AUX
       └─► it       dobj     PRP PRON
 ```

"umbrella" is not a relative pronoun, but if we replace it, we get "The one **you're mom** did it", which doesn't make sense. Using `.left_edge` will catch the usage of "whose".

(Note: This problem can occur with subjects whose parents are `pcomp` or `ccomp`. But, it's hard to make a rule because the replacement can sometimes work.)

---
</details>

```python
            # Insert extra space when replacing the "us" in "Let's"
            lets_ws = token.lower_ in ["s", "'s", "’s"] and not token.nbor(-1).whitespace_
            sub = [(subtree_bounds(token), (" " * lets_ws) + "you're mom")]

            verb = try_verb(parent)
            if verb:
                sub.append(verb)
            yield sub
```

#### Excluded dependencies

<details>
<summary>Why are the rest of the dependencies excluded?</summary>

They just aren't noun-like enough to work without requiring lots of special cases. Of those, though, there are three that deserve further explanation:

* [Agent](https://en.wikipedia.org/wiki/Agent_(grammar)) (`agent`): In a passive construction, the subject switches places with the object and becomes "by [original subject]". This "by [original subject]" is an agent. But, because the `agent` label always points to "by", this case is covered by `pobj`.

  ```text
  Dep tree Token Dep type Tag Part of Sp
  ──────── ───── ──────── ─── ──────────
  ┌─►      I     nsubj    PRP PRON
  ├──      hit   ROOT     VBD VERB
  └─►      him   dobj     PRP PRON

  Dep tree Token Dep type  Tag Part of Sp
  ──────── ───── ───────── ─── ──────────
    ┌──►   He    nsubjpass PRP PRON
    │┌─►   was   auxpass   VBD AUX
  ┌─┴┴──   hit   ROOT      VBN VERB
  └─►┌──   by    agent     IN  ADP
     └─►   me    pobj      PRP PRON
  ```

* Conjunct (`conj`): Something that is coordinated with something else. For example:

  ```text
  Dep tree Token Dep type Tag Part of Sp
  ──────── ───── ──────── ─── ──────────
  ┌──────  Watch ROOT     VB  VERB
  │   ┌─►  the   det      DT  DET
  └─►┌┼──  sun   dobj     NN  NOUN
     │└─►  and   cc       CC  CCONJ
     └──►  moon  conj     NN  NOUN
  ```

  Replacing the `dobj` gives us "Watch **you're mom**". If we could also replace the `conj`, then we could get "Watch the sun and **you're mom**". But, a `conj` can only be replaced when it's coordinated with something else that can be replaced, such as a subject or object. The extra complexity needed to detect that doesn't seem worth it. (See the [`noun_chunks` syntax iterator](https://github.com/explosion/spaCy/blob/master/spacy/lang/en/syntax_iterators.py) for an example of how this might be done.)

* Expletive (`expl`): "An existential there in the subject position." For example:

    * "**There** is a cow."
    * "**There**'s nothing to be afraid of."
    * "Then **there**'s no time to waste!"
    * "**There** are falcons and eagles."

  Sometimes, these work (e.g. the first), but mostly they sound weird. So, we exclude them.

---
</details>

### `ym_sentence`

```python
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
```

<details>
<summary>How do we check if a subject/verb replacement overlaps with other replacements?</summary>

We could individually check if the subject or verb overlap, but that would be complicated. So, we just check once using the bounds of both ranges. This might cause non-overlapping replacements to later be rejected, but in general, it seems that it doesn't. The tokens that occur between a subject and its verb are usually auxillaries or adverbs, not possession modifiers or objects.

---
</details>

<details>
<summary>Doesn't <code>.insert()</code> take O(N)?</summary>

Yes, but the number of replacements per sentence is usually low, so the list is usually short. This means that a list is fast enough. We'd only need a better strategy if we were dealing with large lists. See the [Sorted Containers implementation details](http://www.grantjenks.com/docs/sortedcontainers/implementation.html) for more information.

---
</details>

```python
    if len(sub) > 0:
        return sub

    for token in tokens:
        if token.pos_ in ["NOUN", "PROPN", "PRON"]:
            return [(token_bounds(token), "you're mom")]

    if sent.root.pos_ not in ["PUNCT", "SYM", "X"]:
        return [(token_bounds(sent.root), "you're mom")]

    return []
```

If we can't find any other replacement, we try replacing a random noun. We use `token_bounds` to keep the replacement small—this seems to keep things interesting. Failing that, we replace the root if it isn't punctuation or gibberish. This works surprisingly well for sentence fragments.

### Helpers

```python
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
```

Punctuation is nested in weird ways, so trying to preserve it breaks just as many replacements as it fixes. Still, it makes things a bit more interesting overall.

### Verbs

```python
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
```

These verbs are irregular, auxiliaries, or both. For [contractions](https://en.wikipedia.org/wiki/Contraction_(grammar)#English), we match the style: normal apostrophe, curly apostrophe, or nothing.

```python
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
```

<details>
<summary>What's going on here?</summary>

Subjects are trickier than objects because the verb must agree with subject. (The rest of the sentence might also have to agree with the subject, but that's too complicated to handle.) In our case, the verb must agree with "you're mom", which is third person singular. There are several cases depending on what type of verb we're dealing with:

* Third person singular present (`VBZ`): The verb already agrees with the subject, so we don't have to do anything.
* Modal auxiliary (`MD`): In English, [modal verbs](https://en.wikipedia.org/wiki/English_modal_verbs) don't inflect based on person. So, we don't have to do anything.
* Base form (`VB`): If the sentence is "[subj] do [verb]", we need to change "do" to "does". For example, "I **do** eat" should be come "you're mom **does** eat".
* Gerund or present participle (`VBG`) and past participle (`VBN`): If there isn't a modal verb, then depending on the tense, we may have to change an auxiliary verb. For `VBN`, this may be a passive auxiliary.
* Past tense (`VBD`): If the verb is "were", we need to change it to "was".
* Non-third person singular present: (`VBP`): If the verb is "ai" (from "ain't), we do nothing. If the verb is irregular, we apply one of the replacements from `SPECIAL_VERBS`. Otherwise, we use suffix rules to add `-ies`, `-es`, or `-s` to the verb. This doesn't always work (e.g. "quiz" becomes "quizes" instead of "quizzes"), but it handles most verbs.

---
</details>

### discord.py cog

```python
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
```

The [character limit for a chat message](https://discord.com/developers/docs/resources/channel#create-message-params) is 2000 characters. Specifically, this is [2000 code points](https://github.com/discord/discord-api-docs/issues/1315#issuecomment-577461770), which means that it's safe to use Python's `len()`.

```python
def setup(client):
    client.add_cog(YoureMom())
```

### Discord message formatting

```python
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
```

<details>
<summary>What's the purpose of this?</summary>

To process chat messages, we need to ensure that all markup is correctly [tokenized](https://spacy.io/usage/spacy-101/#annotations-token). That is, given a message like `||hello||`, we want to make sure that the model sees three tokens (`||`, `hello`, `||`) instead of one (`||hello||`). This gives the model a better chance of understanding the message.

Of course, since the model wasn't trained on Discord chat messages, it struggles to handle markup. Symbols like `_` and `||` are often labeled as proper nouns instead of as punctuation. Still, tokenizing the markup is better than nothing. (We could just strip all markup, but that's boring.)

Here are the types of markup that Discord uses:

* [Markdown](https://support.discord.com/hc/en-us/articles/210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline-): Discord's flavor of Markdown includes bold, italic, underline, block quotes, strikethrough, inline code, code blocks, and spoiler tags. The default tokenization rules handle everything except strikethrough and spoiler tags.
  * For strikethrough (`~~strikethrough~~`), we add a rule to split off `~`. We use `~` instead of `~~` because tests show that `~` is consistently recognized as punctuation, whereas `~~` is often incorrectly recognized as a proper noun.
  * For spoiler tags (`||spoiler alert||`), we add a rule to split off `||`. `|` and `||` are equally confusing to the model, but `||` produces one token instead of two. Hopefully, fewer tokens means fewer opportunities for the model to get confused.
* [Mentions and custom emoji](https://discord.com/developers/docs/reference#message-formatting): The default tokenization rules split mentions and custom emoji into several tokens. So, we use the [retokenizer](https://spacy.io/usage/linguistic-features/#retokenization) to merge them back into one token.
* [Auto-embed suppression](https://support.discord.com/hc/en-us/articles/206342858--How-do-I-disable-auto-embed-): `<` and `>` are included in the default tokenization rules.
* Character escaping: We could add rules to split off `\`, but the model probably isn't going to understand either way. So, again, we err on the side of producing fewer tokens.

---
</details>

## Future work

* **you're mom gay**: More research is required to understand this advanced variant.
