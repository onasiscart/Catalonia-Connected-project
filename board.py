from yogi import * 

def read_matrix(rows: int) -> list[list[str]]:
    matrix = []
    for _ in range(rows):
        r = read(str)
        matrix.append(list(r))
    return matrix

def paint_matrix(rows: int, columns: int, matrix: list[list[str]]):
    for _ in range(4):
        for r in range(rows):
            for c in range(columns):
                if matrix[r][c] != '#' and matrix[r][c] != '.':
                    i = j = 1
                    while c + i < columns and matrix[r][c + i] == '.':
                        matrix[r][c + i] = matrix[r][c]
                        i += 1
                    while c - j >= 0 and matrix[r][c - j] == '.':
                        matrix[r][c - j] = matrix[r][c]
                        j += 1
                
                    i = j = 1
                    while r + i < rows and matrix[r + i][c] == '.': 
                        matrix[r + i][c] = matrix[r][c]
                        i += 1
                    while r - j >= 0 and matrix[r - j][c] == '.': 
                        matrix[r - j][c] = matrix[r][c]
                        j += 1               


def main():
    for n_rows in tokens(int):
        n_col = read(int)
        matrix = read_matrix(n_rows)
        paint_matrix(n_rows, n_col, matrix)
        for row in matrix:
            print(''.join(row))
        print()
        

main()