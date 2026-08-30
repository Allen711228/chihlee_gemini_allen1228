# -*- coding: utf-8 -*-
"""
大學數學運算
=====================================================================
本檔案涵蓋大學階段常見的數學運算，並以 Python 程式碼示範，
每一段都會先說明數學原理，再提供程式範例與執行結果。

內容總覽：
  1. 極限與數值微分（微積分）
  2. 數值積分（梯形法與辛普森法）
  3. 矩陣運算（加法、乘法、轉置、行列式、反矩陣）
  4. 複數運算
  5. 統計：常態分布與 z 分數
  6. 線性迴歸（最小平方法）
"""

import math

print("=" * 70)
print("1. 極限與數值微分（微積分）")
print("=" * 70)
# ---------------------------------------------------------------------
# 說明：導數（微分）描述函數在某一點的「瞬間變化率」。
#   數學定義：f'(x) = lim(h→0) [f(x+h) - f(x)] / h
#   數值方法：取很小的 h（例如 10⁻⁶）代入公式近似微分值。
# ---------------------------------------------------------------------
def derivative(f, x: float, h: float = 1e-6) -> float:
    """以差商公式計算函數 f 在 x 的近似導數。"""
    return (f(x + h) - f(x - h)) / (2 * h)  # 中央差商，誤差更小

# 例：f(x) = x²，其導數應為 f'(x) = 2x
def f_square(x):
    return x ** 2

x0 = 3
print(f"f(x) = x²，理論導數 f'({x0}) = 2×{x0} = {2 * x0}")
print(f"數值計算 f'({x0}) ≈ {derivative(f_square, x0):.6f}")

# 例：f(x) = sin(x)，其導數應為 f'(x) = cos(x)
x0 = 1.0
print(f"f(x) = sin(x)，理論導數 f'({x0}) = cos({x0}) = {math.cos(x0):.6f}")
print(f"數值計算 f'({x0}) ≈ {derivative(math.sin, x0):.6f}")

print()
print("=" * 70)
print("2. 數值積分（梯形法與辛普森法）")
print("=" * 70)
# ---------------------------------------------------------------------
# 說明：積分代表「曲線下面積」，常用於計算面積、距離、總量。
#   定積分 ∫ₐᵇ f(x)dx 的幾何意義是 x 軸與曲線之間的面積。
#   梯形法：把區間切成 n 段，用 n 個梯形近似面積。
#   辛普森法：用拋物線近似，精確度更高（適合 n 為偶數）。
# ---------------------------------------------------------------------
def trapezoid(f, a: float, b: float, n: int = 1000) -> float:
    """以梯形法求 ∫ₐᵇ f(x) dx 的近似值。"""
    h = (b - a) / n
    total = (f(a) + f(b)) / 2
    for i in range(1, n):
        total += f(a + i * h)
    return total * h

def simpson(f, a: float, b: float, n: int = 1000) -> float:
    """以辛普森法求 ∫ₐᵇ f(x) dx 的近似值（n 需為偶數）。"""
    if n % 2 == 1:
        n += 1
    h = (b - a) / n
    total = f(a) + f(b)
    for i in range(1, n):
        total += f(a + i * h) * (4 if i % 2 == 1 else 2)
    return total * h / 3

# 例：∫₀¹ x² dx = 1/3 ≈ 0.3333...
print("∫₀¹ x² dx 的理論值 = 1/3 ≈", round(1 / 3, 6))
print(f"梯形法近似值   ≈ {trapezoid(f_square, 0, 1):.6f}")
print(f"辛普森法近似值 ≈ {simpson(f_square, 0, 1):.6f}")

# 例：∫₀^π sin(x) dx = 2
print("∫₀^π sin(x) dx 的理論值 = 2")
print(f"辛普森法近似值 ≈ {simpson(math.sin, 0, math.pi):.6f}")

print()
print("=" * 70)
print("3. 矩陣運算（加法、乘法、轉置、行列式、反矩陣）")
print("=" * 70)
# ---------------------------------------------------------------------
# 說明：矩陣是「排列成矩形的一組數字」，是線性代數的核心工具。
#   加法：相同位置的元素相加（兩矩陣維度必須相同）
#   乘法：(A×B)[i][j] = Σₖ A[i][k]·B[k][j]（A 的行數必須等於 B 的列數）
#   轉置：把行與列互換
#   行列式：方陣的特徵純量，非零才存在反矩陣
# ---------------------------------------------------------------------
def matrix_add(A, B):
    """矩陣加法。"""
    return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]

def matrix_multiply(A, B):
    """矩陣乘法。"""
    rows_a, cols_a = len(A), len(A[0])
    rows_b, cols_b = len(B), len(B[0])
    assert cols_a == rows_b, "A 的行數必須等於 B 的列數"
    result = [[0] * cols_b for _ in range(rows_a)]
    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a):
                result[i][j] += A[i][k] * B[k][j]
    return result

def transpose(A):
    """矩陣轉置。"""
    return [[A[i][j] for i in range(len(A))] for j in range(len(A[0]))]

def determinant(A):
    """計算方陣的行列式（使用餘因子展開）。"""
    n = len(A)
    if n == 1:
        return A[0][0]
    if n == 2:
        return A[0][0] * A[1][1] - A[0][1] * A[1][0]
    total = 0
    for col in range(n):
        minor = [row[:col] + row[col + 1:] for row in A[1:]]
        total += ((-1) ** col) * A[0][col] * determinant(minor)
    return total

def inverse(A):
    """求 2×2 矩陣的反矩陣（使用伴隨矩陣法）。"""
    det = determinant(A)
    assert det != 0, "行列式為 0，矩陣不可逆"
    return [
        [A[1][1] / det, -A[0][1] / det],
        [-A[1][0] / det, A[0][0] / det],
    ]

A = [[1, 2], [3, 4]]
B = [[5, 6], [7, 8]]
print(f"A = {A}")
print(f"B = {B}")
print(f"A + B = {matrix_add(A, B)}")
print(f"A × B = {matrix_multiply(A, B)}")
print(f"Aᵀ = {transpose(A)}（轉置）")
print(f"det(A) = {determinant(A)}（行列式）")
print(f"A⁻¹ = {inverse(A)}（反矩陣）")
# 驗證：A × A⁻¹ 應等於單位矩陣 I = [[1,0],[0,1]]
identity = matrix_multiply(A, inverse(A))
print(f"驗證 A × A⁻¹ = {[[round(v, 6) for v in row] for row in identity]} ≈ 單位矩陣")

print()
print("=" * 70)
print("4. 複數運算")
print("=" * 70)
# ---------------------------------------------------------------------
# 說明：複數 z = a + bi，其中 i = √-1。
#   加減：實部、虛部分別運算
#   乘法：(a+bi)(c+di) = (ac - bd) + (ad + bc)i
#   模長（大小）：|z| = √(a² + b²)
#   共軛複數：實部不變、虛部變號，z̄ = a - bi
# ---------------------------------------------------------------------
z1 = complex(3, 4)      # 3 + 4i
z2 = complex(1, -2)     # 1 - 2i

print(f"z₁ = {z1}，z₂ = {z2}")
print(f"z₁ + z₂ = {z1 + z2}")
print(f"z₁ - z₂ = {z1 - z2}")
print(f"z₁ × z₂ = {z1 * z2}")
print(f"|z₁| = {abs(z1)}（模長，√(3²+4²)=5）")
print(f"z₁ 的共軛 = {z1.conjugate()}")

print()
print("=" * 70)
print("5. 統計：常態分布與 z 分數")
print("=" * 70)
# ---------------------------------------------------------------------
# 說明：
#   常態分布：中間高兩邊低、左右對稱的鐘形分布，以平均數 μ 與
#   標準差 σ 描述。約 68% 資料落在 μ±σ，95% 落在 μ±2σ。
#   z 分數：z = (x - μ) / σ，衡量資料距離平均數幾個標準差。
# ---------------------------------------------------------------------
mu, sigma = 70, 10      # 某次考試平均 70 分、標準差 10 分
x_student = 85
z = (x_student - mu) / sigma
print(f"平均 μ = {mu}、標準差 σ = {sigma}、學生分數 x = {x_student}")
print(f"z 分數 = ({x_student} - {mu}) / {sigma} = {z}")
print(f"  該生分數比平均高 {z} 個標準差")

# 標準常態分布的機率密度函數 f(x) = 1/(σ√(2π)) · e^(-(x-μ)²/(2σ²))
def normal_pdf(x, mu, sigma):
    return (1 / (sigma * math.sqrt(2 * math.pi))) * math.exp(-((x - mu) ** 2) / (2 * sigma ** 2))

print(f"x = {mu} 時的機率密度 f({mu}) ≈ {normal_pdf(mu, mu, sigma):.4f}（鐘形頂點）")

print()
print("=" * 70)
print("6. 線性迴歸（最小平方法）")
print("=" * 70)
# ---------------------------------------------------------------------
# 說明：線性迴歸找出一條直線 y = a + bx，最「貼近」資料點。
#   最小平方法：讓「預測值與實際值的平方差總和」最小。
#   斜率 b = Σ(xᵢ-x̄)(yᵢ-ȳ) / Σ(xᵢ-x̄)²
#   截距 a = ȳ - b·x̄
# ---------------------------------------------------------------------
def linear_regression(xs, ys):
    """以最小平方法回傳 (斜率 b, 截距 a)。"""
    n = len(xs)
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    numerator = sum((xs[i] - x_mean) * (ys[i] - y_mean) for i in range(n))
    denominator = sum((xs[i] - x_mean) ** 2 for i in range(n))
    b = numerator / denominator
    a = y_mean - b * x_mean
    return b, a

xs = [1, 2, 3, 4, 5]
ys = [2, 4, 5, 4, 5]
slope, intercept = linear_regression(xs, ys)
print(f"資料點：(x, y) = {list(zip(xs, ys))}")
print(f"迴歸直線：y = {intercept:.2f} + {slope:.2f}x")
# 預測 x = 6 時的 y 值
pred = slope * 6 + intercept
print(f"預測 x = 6 時，y ≈ {pred:.2f}")
