
public class MathOps {
    public static int max(int[] nums) {
        int max = nums[0];
        for (int n : nums)
            if (n > max) max = n;
        return max;
    }

    public static int min(int[] nums) {
        int min = nums[0];
        for (int n : nums)
            if (n < min) min = n;
        return min;
    }

    public static int avg(int[] nums) {
        int sum = 0;
        for (int n : nums) sum += n;
        return sum / nums.length;
    }
}
