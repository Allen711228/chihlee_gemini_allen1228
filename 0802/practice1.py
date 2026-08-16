# 學生成績計算系統

def get_grade(score):
    """根據分數回傳等第"""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def input_students():
    """輸入學生資料，回傳學生列表"""
    students = []
    print("=== 學生成績輸入系統 ===")
    print("（輸入學生姓名為空白時結束輸入）\n")

    while True:
        name = input("請輸入學生姓名：").strip()
        if not name:
            break

        scores = []
        subjects = ["國文", "英文", "數學", "自然", "社會"]
        for subject in subjects:
            while True:
                try:
                    score = float(input(f"  {subject} 成績（0~100）："))
                    if 0 <= score <= 100:
                        scores.append(score)
                        break
                    else:
                        print("  ！請輸入 0 到 100 之間的數字")
                except ValueError:
                    print("  ！請輸入有效的數字")

        average = sum(scores) / len(scores)
        students.append({
            "name": name,
            "scores": dict(zip(subjects, scores)),
            "average": round(average, 2),
            "grade": get_grade(average)
        })
        print(f"  ✔ {name} 輸入完成，平均：{average:.2f}，等第：{get_grade(average)}\n")

    return students


def show_report(students):
    """顯示成績報表"""
    if not students:
        print("沒有任何學生資料。")
        return

    subjects = ["國文", "英文", "數學", "自然", "社會"]

    print("\n" + "=" * 60)
    print("               學生成績報表")
    print("=" * 60)

    # 表頭
    header = f"{'姓名':<8}" + "".join(f"{s:>6}" for s in subjects) + f"{'平均':>8}  {'等第':>4}"
    print(header)
    print("-" * 60)

    # 每位學生
    for student in students:
        row = f"{student['name']:<8}"
        for subject in subjects:
            row += f"{student['scores'][subject]:>6.1f}"
        row += f"{student['average']:>8.2f}  {student['grade']:>4}"
        print(row)

    print("-" * 60)

    # 各科平均
    subject_avgs = {
        s: sum(stu["scores"][s] for stu in students) / len(students)
        for s in subjects
    }
    avg_row = f"{'全班平均':<8}" + "".join(f"{subject_avgs[s]:>6.1f}" for s in subjects)
    class_avg = sum(stu["average"] for stu in students) / len(students)
    avg_row += f"{class_avg:>8.2f}"
    print(avg_row)

    print("=" * 60)

    # 統計摘要
    best = max(students, key=lambda s: s["average"])
    worst = min(students, key=lambda s: s["average"])

    print(f"\n📊 統計摘要")
    print(f"  學生人數：{len(students)} 人")
    print(f"  全班平均：{class_avg:.2f}")
    print(f"  最高分：{best['name']}（{best['average']:.2f}）")
    print(f"  最低分：{worst['name']}（{worst['average']:.2f}）")

    # 等第分布
    grade_count = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for student in students:
        grade_count[student["grade"]] += 1

    print(f"\n  等第分布：")
    for grade, count in grade_count.items():
        bar = "█" * count
        print(f"    {grade}：{bar} ({count} 人)")

    print("=" * 60)


def main():
    students = input_students()
    show_report(students)


if __name__ == "__main__":
    main()
