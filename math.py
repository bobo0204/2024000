import random

def generate_question():
    while True:
        # 隨機生成三個個位數的數字
        num1 = random.randint(1, 9)
        num2 = random.randint(1, 9)
        num3 = random.randint(1, 9)
        
        # 隨機選擇兩個運算符
        operators = ['+', '-', '*', '/']
        operator1 = random.choice(operators)
        operator2 = random.choice(operators)

        # 構建運算表達式
        expression = f"{num1} {operator1} {num2} {operator2} {num3}"
        
        # 計算正確答案
        try:
            correct_answer = eval(expression)
            # 確認答案為整數且無餘數
            if correct_answer == int(correct_answer):
                return expression, int(correct_answer)
        except ZeroDivisionError:
            continue
        except SyntaxError:
            continue

def main():
    while True:
        # 生成一個隨機題目
        expression, correct_answer = generate_question()
        
        # 提示用戶輸入答案
        print(f"請計算：{expression}")
        
        while True:
            user_answer = input("你的答案是：")
            
            try:
                user_answer = int(user_answer)
            except ValueError:
                print("請輸入有效的整數答案。")
                continue
            
            if user_answer == correct_answer:
                print("很棒，正確 ~")
                break
            else:
                print(f"錯誤，加油，再想想 ~")

if __name__ == "__main__":
    main()
