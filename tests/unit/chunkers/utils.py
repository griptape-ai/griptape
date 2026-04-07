from griptape.tokenizers import BaseTokenizer


def gen_paragraph(max_tokens: int, tokenizer: BaseTokenizer, sentence_separator: str) -> str:
    all_text = ""
    word = "foo"
    index = 0

    def add_word(base, w, i):
        return sentence_separator.join([base, f"{w}-{i}"])

    while max_tokens >= tokenizer.count_tokens(add_word(all_text, word, index)):
        all_text = f"{word}-{index}" if all_text == "" else add_word(all_text, word, index)
        index += 1

    return all_text + sentence_separator
