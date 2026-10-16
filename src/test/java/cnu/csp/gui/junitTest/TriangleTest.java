package cnu.csp.gui.junitTest;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.CsvFileSource;
import org.junit.jupiter.params.provider.MethodSource;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * 软件测试实验二：边界值分析方法
 * 针对三角形判断程序 Triangle.classify(a, b, c)（输入范围 1~100），
 * 分别采用 4 种边界值分析方法设计测试用例，并使用 JUnit5 参数化测试实现：
 *
 *   1. 一般边界值方法           4n+1  = 13 个测试用例
 *   2. 健壮性边界值方法         6n+1  = 19 个测试用例
 *   3. 最坏情况一般边界值方法   5^n   = 125 个测试用例
 *   4. 最坏情况健壮性边界值方法 7^n   = 343 个测试用例
 *
 * 其中 n = 3（三个输入变量），变量边界为 [1, 100]，取离边界最近的合法值 1、2、99、100，
 * 健壮性再向外各扩展一个非法值 0、101，默认 Nom 值取 50。
 */
public class TriangleTest {

    private static final int MIN = 1;
    private static final int MAX = 100;
    private static final int NOM = 50;

    // ===================== 测试用例的期望值判定（独立于被测代码的判定规则） =====================

    /** 按题目判定规则独立推导期望输出，避免与被测代码同源 */
    private static String expected(int a, int b, int c) {
        if (a < MIN || a > MAX || b < MIN || b > MAX || c < MIN || c > MAX) {
            return "输入错误";
        }
        int max = Math.max(a, Math.max(b, c));
        int sum = a + b + c;
        if (max >= sum - max) {          // 最大边 >= 其余两边之和，不构成三角形
            return "非三角形";
        }
        if (a == b && b == c) {
            return "等边三角形";
        }
        if (a == b || b == c || a == c) {
            return "等腰三角形";
        }
        return "一般三角形";
    }

    /** 生成笛卡尔积测试数据（以 Arguments.of 形式提供三个参数） */
    private static Stream<Arguments> cartesian(int[] values) {
        List<Arguments> result = new ArrayList<>();
        for (int a : values) {
            for (int b : values) {
                for (int c : values) {
                    result.add(Arguments.of(a, b, c));
                }
            }
        }
        return result.stream();
    }

    // ===================== 0. 课程示例：@CsvSource 用法演示 =====================

    @ParameterizedTest
    @CsvSource({
            "1,2,1,非三角形",
            "-1,2,3,输入错误"
    })
    void testWithCsvSource(int a, int b, int c, String expected) {
        assertEquals(expected, Triangle.classify(a, b, c));
    }

    // ===================== 0. 课程示例：@CsvFileSource 用法演示 =====================

    @ParameterizedTest
    @CsvFileSource(resources = "/triangle-cases.csv", numLinesToSkip = 1)
    void test_csv_file_source(int a, int b, int c, String expected) {
        assertEquals(expected, Triangle.classify(a, b, c));
    }

    // ===================== 3.1 一般边界值方法（4n+1 = 13） =====================

    static Stream<Arguments> generalBvaCases() {
        List<Arguments> cases = new ArrayList<>();
        for (int v : new int[]{MIN, MIN + 1, NOM, MAX - 1, MAX}) {
            cases.add(Arguments.of(v, NOM, NOM));   // 变量 a 取边界值
            cases.add(Arguments.of(NOM, v, NOM));   // 变量 b 取边界值
            cases.add(Arguments.of(NOM, NOM, v));   // 变量 c 取边界值
        }
        cases.add(Arguments.of(NOM, NOM, NOM));     // 全部取 Nom，去重后共 4n+1 = 13 个
        return cases.stream();
    }

    @ParameterizedTest(name = "[{index}] classify({0}, {1}, {2})")
    @MethodSource("generalBvaCases")
    void test_general_bva(int a, int b, int c) {
        assertEquals(expected(a, b, c), Triangle.classify(a, b, c));
    }

    // ===================== 3.2 健壮性边界值方法（6n+1 = 19） =====================

    static Stream<Arguments> robustBvaCases() {
        List<Arguments> cases = new ArrayList<>();
        for (int v : new int[]{MIN - 1, MIN, MIN + 1, NOM, MAX - 1, MAX, MAX + 1}) { // 0,1,2,50,99,100,101
            cases.add(Arguments.of(v, NOM, NOM));
            cases.add(Arguments.of(NOM, v, NOM));
            cases.add(Arguments.of(NOM, NOM, v));
        }
        cases.add(Arguments.of(NOM, NOM, NOM));     // 6n+1 = 19 个
        return cases.stream();
    }

    @ParameterizedTest(name = "[{index}] classify({0}, {1}, {2})")
    @MethodSource("robustBvaCases")
    void test_robust_bva(int a, int b, int c) {
        assertEquals(expected(a, b, c), Triangle.classify(a, b, c));
    }

    // ===================== 3.3 最坏情况一般边界值方法（5^3 = 125） =====================

    static Stream<Arguments> worstCaseGeneralBvaCases() {
        return cartesian(new int[]{MIN, MIN + 1, NOM, MAX - 1, MAX});
    }

    @ParameterizedTest(name = "[{index}] classify({0}, {1}, {2})")
    @MethodSource("worstCaseGeneralBvaCases")
    void test_worst_case_general_bva(int a, int b, int c) {
        assertEquals(expected(a, b, c), Triangle.classify(a, b, c));
    }

    // ===================== 3.4 最坏情况健壮性边界值方法（7^3 = 343） =====================

    static Stream<Arguments> worstCaseRobustBvaCases() {
        return cartesian(new int[]{MIN - 1, MIN, MIN + 1, NOM, MAX - 1, MAX, MAX + 1});
    }

    @ParameterizedTest(name = "[{index}] classify({0}, {1}, {2})")
    @MethodSource("worstCaseRobustBvaCases")
    void test_worst_case_robust_bva(int a, int b, int c) {
        assertEquals(expected(a, b, c), Triangle.classify(a, b, c));
    }
}
