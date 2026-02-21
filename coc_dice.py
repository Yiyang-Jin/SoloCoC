"""CoC 骰子系统：支持 D100、D6、3D6×5 等常见骰型。"""
import random
import re

# 常见 CoC 骰型：1D100, 1D6, 3D6, 3D6×5 等
_DICE_PATTERN = re.compile(
    r"^(?:(\d+)\s*d\s*(\d+)\s*(?:[×x]\s*(\d+))?|(\d+)\s*d\s*(\d+))$",
    re.IGNORECASE,
)


def roll_d100() -> int:
    """投 1D100（1-100）。"""
    return random.randint(1, 100)


def roll_d6() -> int:
    """投 1D6。"""
    return random.randint(1, 6)


def roll_3d6() -> int:
    """投 3D6。"""
    return sum(random.randint(1, 6) for _ in range(3))


def roll_3d6x5() -> int:
    """投 3D6×5（用于 Luck 等）。"""
    return roll_3d6() * 5


def roll(expr: str) -> tuple[int, str]:
    """
    解析并投骰。支持格式：1D100, 3D6, 3D6×5 等。
    返回 (结果, 描述字符串)。
    """
    expr = expr.strip().lower().replace(" ", "")
    m = re.match(r"^(\d*)d(\d+)(?:[×x](\d+))?$", expr)
    if not m:
        raise ValueError(f"不支持的骰子格式: {expr}，示例: 1d100, 3d6, 3d6×5")

    n = int(m.group(1)) if m.group(1) else 1
    sides = int(m.group(2))
    mult = int(m.group(3)) if m.group(3) else 1

    if n < 1 or n > 100 or sides < 2 or sides > 1000 or mult < 1 or mult > 1000:
        raise ValueError("骰子参数超出范围")

    rolls = [random.randint(1, sides) for _ in range(n)]
    total = sum(rolls) * mult

    if n == 1 and mult == 1:
        desc = f"D{sides} = {total}"
    elif mult == 1:
        desc = f"{n}D{sides} = {'+'.join(map(str, rolls))} = {total}"
    else:
        desc = f"{n}D{sides}×{mult} = ({'+'.join(map(str, rolls))})×{mult} = {total}"

    return total, desc


def roll_skill_check(skill_value: int) -> tuple[bool, int, str]:
    """
    技能检定：投 D100，与技能值比较。
    返回 (是否成功, 投出值, 描述)。
    """
    r, desc = roll("1d100")
    success = r <= skill_value
    return success, r, desc


def roll_3d6_for_attribute() -> tuple[int, str]:
    """投 3D6 作为属性值（用于人物卡生成）。"""
    v = roll_3d6()
    return v, f"3D6 = {v}"
