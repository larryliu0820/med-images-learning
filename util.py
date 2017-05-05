

def binary_search(data, val):
    high_index = len(data) - 1
    low_index = 0
    while high_index > low_index:
        index = (high_index + low_index) / 2
        sub = data[index]
        if data[low_index] == val:
            return [low_index, low_index]
        elif sub == val:
            return [index, index]
        elif data[high_index] == val:
            return [high_index, high_index]
        elif sub > val:
            if high_index == index:
                return sorted([high_index, low_index])
            high_index = index
        else:
            if low_index == index:
                return sorted([high_index, low_index])
            low_index = index
    return sorted([high_index, low_index])


def sign(p1, p2, p3):
    return (p1.xcor - p3.xcor) * (p2.ycor - p3.ycor) - (p2.xcor - p3.xcor) * (p1.ycor - p3.ycor)


def point_in_triangle(p, p1, p2, p3):
    b1 = sign(p, p1, p2) < 0
    b2 = sign(p, p2, p3) < 0
    b3 = sign(p, p3, p1) < 0
    return b1 == b2 and b2 == b3

