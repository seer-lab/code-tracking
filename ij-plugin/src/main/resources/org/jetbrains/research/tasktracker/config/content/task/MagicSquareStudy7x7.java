public class MagicSquareStudy7x7 {

    public static void main(String[] args) {
        // A valid 7x7 Magic Square (Magic Constant = 175)
        int[][] square = {
                {22, 47, 16, 41, 10, 35, 4},
                {5, 23, 48, 17, 42, 11, 29,},
                {30, 6, 24, 49, 18, 36, 12},
                {13, 31, 7, 25, 43, 19, 37},
                {38, 14, 32, 1, 26, 44, 20},
                {21, 39, 8, 33, 2, 27, 45},
                {46, 15, 40, 9, 34, 3, 28}
        };

        // The magic constant for a 7x7 square using numbers 1-49 is 175
        int targetSum = 175;

        if (isMagicSquare(square, targetSum)) {
            System.out.println("Result: This is a valid 7x7 Magic Square!");
        } else {
            System.out.println("Result: Not a Magic Square.");
        }
    }

    public static boolean isMagicSquare(int[][] matrix, int sum) {
        // TODO: BUG FIX (Step 1)
        int n = matrix.length ;


        // 1. Check Horizontal Sums (Rows)
        for (int i = 0; i < n; i++) {
            int rowSum = 0;
            for (int j = 0; j < n; j++) {
                rowSum += matrix[i][j];
            }
            if (rowSum != sum) return false;
        }

        // 2. Check Vertical Sums (Columns)
        for (int j = 0; j < n; j++) {
            int colSum = 0;
            for (int i = 0; i < n; i++) {
                colSum += matrix[i][j];
            }
            if (colSum != sum) return false;
        }

        // TODO STUDENT TASK: Check if diagonals satisfy the criteria for magic square (Step 2)


        return true;
    }
}