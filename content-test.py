import json
import argparse


def load_mirrors(content):
    content = content.replace("'", '"')
    data = json.loads(content)
    return data.get("hub-mirror")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="My Python script")
    parser.add_argument("--content", type=str, required=True, help="content")
    # 解析参数
    args = parser.parse_args()
    a = load_mirrors(args.content)
    print(a)
