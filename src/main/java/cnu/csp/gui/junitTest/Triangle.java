/**
 * @Title: Triangle.java
 * @Package cnu.csp.gui.junitTest
 * @Description: 判断三角形是否为三角形，等腰或等边或不等三角形，或不是三角形
 * @author tiger
 * @version V1.8
 */
package cnu.csp.gui.junitTest;

public class Triangle {

    /**
     * 判断三角形类型。
     * 输入为三个整数 a、b、c，分别作为三角形的三条边。
     * 取值范围：1 ~ 100（含边界）。
     *
     * 判定规则（按题目要求顺序）：
     *   1. 只要有一个数不在 [1,100] 内      -> "输入错误"
     *   2. 不满足任意两边之和大于第三边      -> "非三角形"
     *   3. a == b && b == c                 -> "等边三角形"
     *   4. a == b || a == c || b == c       -> "等腰三角形"
     *   5. 其余情况                          -> "一般三角形"
     */
    public static String classify(int a, int b, int c) {
        // 条件1：输入有效性判断（边界：1 和 100）
        if (a < 1 || a > 100 || b < 1 || b > 100 || c < 1 || c > 100) {
            return "输入错误";
        }
        // 条件2：三角形不等式，两边之和必须大于第三边
        if (!((a + b > c) && (a + c > b) && (b + c > a))) {
            return "非三角形";
        }
        if (a == b && b == c) {
            return "等边三角形";
        } else if (a == b || a == c || b == c) {
            return "等腰三角形";
        } else {
            return "一般三角形";
        }
    }
}
