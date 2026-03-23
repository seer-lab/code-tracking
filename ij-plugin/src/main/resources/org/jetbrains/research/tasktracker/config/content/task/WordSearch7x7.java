public class WordSearch7x7 {
    public static void main(String[] args) {
        // 7x7 grid for the study
        char[][] board = {
                {'R', 'A', 'D', 'A', 'R', 'Q', 'P'},
                {'S', 'O', 'L', 'A', 'R', 'W', 'E'},
                {'G', 'B', 'I', 'N', 'A', 'R', 'Y'},
                {'M', 'A', 'T', 'R', 'I', 'X', 'Z'},
                {'V', 'E', 'C', 'T', 'O', 'R', 'K'},
                {'P', 'I', 'X', 'E', 'L', 'S', 'B'},
                {'L', 'O', 'G', 'I', 'C', 'A', 'L'}
        };

        // Test word: "BINARY" (Horizontal at row 2, col 1)
        // Test word: "RADAR" (Horizontal at row 0, col 0)
        String target = "BINARY";
        int[] result = searchWord(board, target);

        if (result != null) {
            System.out.println("Word '" + target + "' found at: Row " + result[0] + ", Col " + result[1]);
        } else {
            System.out.println("Word not found.");
        }
    }

    public static int[] searchWord(char[][] grid, String word) {
        int rows = grid.length;
        int cols = grid[0].length;

        int[][] directions = {
                {0, 1}, {0, -1}, {1, 0}, {-1, 0},   // Horizontal & Vertical
                {1, 1}, {1, -1}, {-1, 1}, {-1, -1} // Diagonals
        };

        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                // Optimization: check first letter match
                if (grid[r][c] == word.charAt(0)) {
                    for (int[] dir : directions) {
                        if (checkDirection(grid, word, r, c, dir[0], dir[1])) {
                            return new int[]{r, c};
                        }
                    }
                }
            }
        }
        return null;
    }

    public static boolean checkDirection(char[][] grid, String word, int r, int c, int dr, int dc) {
        int rows = grid.length;
        int cols = grid[0].length;

        for (int i = 0; i < word.length(); i++) {
            int currR = r + i * dr;
            int currC = c + i * dc;

            // TODO: BUG FIX AREA (Step 1)

            if (currR < 0 || currR >= rows || currC < 0 || currC > cols) {
                return false;
            }

            // TODO: STUDENT TASK AREA (Step 2)


        }
        return true;
    }
}