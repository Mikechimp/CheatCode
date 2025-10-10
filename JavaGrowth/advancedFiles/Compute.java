
import java.util.*;

public class Compute {
    public static void main(String[] args) {
        Scanner s = new Scanner(System.in);
        int[] nums = new int[10];

        for (int i = 0; i < 10; i++) {
            System.out.print("Enter a number: ");
            nums[i] = s.nextInt();
        }

        System.out.println("Maximum: " + MathOps.max(nums));
        System.out.println("Minimum: " + MathOps.min(nums));
        System.out.println("Average: " + MathOps.avg(nums));
    }
}
