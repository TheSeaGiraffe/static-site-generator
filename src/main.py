from textnode import TextNode, TextType


def main():
    text = "This is just a test"
    text_type = TextType.NORMAL
    url = "https://www.homestarrunner.com"

    t_node = TextNode(text, text_type, url)
    print(t_node)


if __name__ == "__main__":
    main()
