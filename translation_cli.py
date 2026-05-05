import json
import random
import time
import os

DATA_FILE = "data/data.json"   # 保存到 data/ 目录
WORDS_FILE = "words.txt"        # 格式: 英文\t中文

def load_words():
    words = []
    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        for line in f.readlines():
            if line.strip() and "\t" in line:
                eng, chn = line.strip().split("\t", 1)
                words.append({"eng": eng, "chn": chn})
    return words

def load_data(words):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {w["eng"]: {"correct": 0, "wrong": 0, "last_seen": 0} for w in words}

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def calc_weight(info):
    now = time.time()
    return info["wrong"] * 2 + (now - info["last_seen"]) * 0.0001 - info["correct"] * 0.5

def pick_word(data, words, last_word=None, only_wrong=False):
    candidates = words
    if only_wrong:
        candidates = [w for w in words if data[w["eng"]]["wrong"] > 0]
        if not candidates:
            print("暂无错词，本次使用全量词库")
            candidates = words

    if last_word in candidates and len(candidates) > 1:
        candidates = [w for w in candidates if w != last_word]

    weights = [max(0.1, calc_weight(data[w["eng"]])) for w in candidates]
    return random.choices(candidates, weights=weights, k=1)[0]

def translation_mode(data, words, direction="eng2chn", only_wrong=False):
    total = 0
    correct_count = 0
    last_word = None

    print("\n🎯 开始翻译练习（输入 q 退出）")

    while True:
        word = pick_word(data, words, last_word, only_wrong)
        last_word = word

        if direction == "eng2chn":
            prompt = f"翻译成中文: {word['eng']}\n答案（q退出）："
            correct_answer = word["chn"]
        else:
            prompt = f"翻译成英文: {word['chn']}\n答案（q退出）："
            correct_answer = word["eng"]

        user_input = input(prompt).strip()
        if user_input.lower() == "q":
            break

        total += 1
        if user_input.lower() == correct_answer.lower():
            print("✅ 正确")
            data[word["eng"]]["correct"] += 1
            correct_count += 1
        else:
            print(f"❌ 错误，正确答案是: {correct_answer}")
            data[word["eng"]]["wrong"] += 1

        data[word["eng"]]["last_seen"] = time.time()
        save_data(data)
        print(f"📊 当前正确率：{correct_count}/{total} = {correct_count/total:.2%}")
        print("-" * 30)

def show_stats(data):
    total = sum(v["correct"] + v["wrong"] for v in data.values())
    correct = sum(v["correct"] for v in data.values())

    print("\n📊 总体统计")
    print("-" * 20)
    print(f"总练习次数：{total}")
    if total > 0:
        print(f"正确率：{correct/total:.2%}")

def show_wrong_words(data):
    wrong_words = [w for w, v in data.items() if v["wrong"] > 0]
    print("\n📚 错词本")
    print("-" * 20)
    if not wrong_words:
        print("暂无错词")
        return
    for w in wrong_words:
        print(f"{w}（错 {data[w]['wrong']} 次）")

def main():
    words = load_words()
    data = load_data(words)

    while True:
        print("\n====================")
        print("🌐 英汉互译小工具")
        print("====================")
        print("1️⃣ 英译汉练习")
        print("2️⃣ 汉译英练习")
        print("3️⃣ 查看统计")
        print("4️⃣ 查看错词本")
        print("5️⃣ 退出")

        choice = input("请选择：").strip()
        if choice == "1":
            translation_mode(data, words, direction="eng2chn")
        elif choice == "2":
            translation_mode(data, words, direction="chn2eng")
        elif choice == "3":
            show_stats(data)
        elif choice == "4":
            show_wrong_words(data)
        elif choice == "5":
            save_data(data)
            print("已保存，退出程序")
            break
        else:
            print("输入无效，请重试")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已退出程序")