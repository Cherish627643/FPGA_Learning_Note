# generate 生成语句

`generate` 是 Verilog 里的**生成语句**，用来在**编译/综合时批量复制硬件结构**，或者根据参数选择生成不同电路。

一句话：

> **`generate` 不是运行时循环，而是“画电路时批量复制”或“按参数选择画哪块电路”。**

类比：

- 数电里：同一块电路要重复 8 次，你不可能手画 8 遍，`generate for` 就是帮你自动复制 8 份。
- C 语言里：像宏展开或模板实例化，编译时展开，不是运行时循环。

---

## 1. 三种 generate

| 类型 | 作用 |
|---|---|
| `generate for` | 批量复制硬件结构 |
| `generate if` | 根据常量条件选择生成哪块电路 |
| `generate case` | 根据常量多路选择生成哪块电路 |

它们都写在模块顶层，和 `assign`、`always`、模块实例化同级。  
不能写在 `always` 或 `initial` 里面。

---

## 2. generate for

### 语法

```verilog
genvar i;
generate
    for (i = 0; i < N; i = i + 1) begin : 块名
        // 要复制的结构
    end
endgenerate
```

`genvar` 是生成循环变量，只能是常量循环。  
`begin : 块名` 必须命名，方便层次化引用和调试。

### 例子：批量生成 8 个 D 触发器

```verilog
module gen_ff(
    input  wire       clk,
    input  wire       rst_n,
    input  wire [7:0] d,
    output reg  [7:0] q
);

    genvar i;
    generate
        for (i = 0; i < 8; i = i + 1) begin : gen_ff
            always @(posedge clk or negedge rst_n) begin
                if (!rst_n)
                    q[i] <= 1'b0;
                else
                    q[i] <= d[i];
            end
        end
    endgenerate

endmodule
```

综合出来就是 8 个独立的 D 触发器。  
`gen_ff[0]`、`gen_ff[1]` … 是层次名。

### 例子：批量例化模块

```verilog
module gen_adder(
    input  wire [3:0] a,
    input  wire [3:0] b,
    output wire [3:0] sum
);

    genvar i;
    generate
        for (i = 0; i < 4; i = i + 1) begin : gen_add
            adder u_adder (
                .a   (a[i]),
                .b   (b[i]),
                .sum (sum[i])
            );
        end
    endgenerate

endmodule
```

等价于手写 4 次 `adder` 实例化。

---

## 3. generate if

根据**常量条件**选择生成哪块电路。条件通常是 `parameter` 或 `localparam`。

```verilog
module gen_if #(
    parameter WIDTH = 8
)(
    input  wire [WIDTH-1:0] a,
    input  wire [WIDTH-1:0] b,
    output wire [WIDTH-1:0] y
);

    generate
        if (WIDTH == 8) begin : gen_8
            assign y = a + b;
        end else if (WIDTH == 16) begin : gen_16
            assign y = a + b;
        end else begin : gen_default
            assign y = a;
        end
    endgenerate

endmodule
```

注意：`WIDTH` 必须是常量，不能是运行时变量。

---

## 4. generate case

```verilog
generate
    case (MODE)
        0: begin : mode0
            assign y = a + b;
        end
        1: begin : mode1
            assign y = a - b;
        end
        default: begin : mode_default
            assign y = a;
        end
    endcase
endgenerate
```

`MODE` 也必须是常量。

---

## 5. generate for 和 always 里的 for 有什么区别

这是最容易混的地方。

| 对比 | generate for | always 里的 for |
|---|---|---|
| 位置 | 模块顶层 | `always` 过程块里 |
| 循环变量 | `genvar` | `integer` |
| 作用 | 复制硬件结构 | 描述过程赋值 |
| 能否例化模块 | 可以 | 不可以 |
| 能否写 `assign` | 可以 | 不可以 |
| 能否写 `always` | 可以 | 不适用 |
| 综合时 | 展开成多份硬件 | 也展开成多份逻辑 |
| 典型用途 | 批量例化、批量 always | 多位赋值、循环计算 |

例子：

```verilog
// generate for：批量生成 always
genvar i;
generate
    for (i = 0; i < 8; i = i + 1) begin : gen_ff
        always @(posedge clk)
            q[i] <= d[i];
    end
endgenerate
```

```verilog
// always 里的 for：在一个 always 里循环赋值
integer i;
always @(*) begin
    for (i = 0; i < 8; i = i + 1)
        y[i] = a[i] & b[i];
end
```

---

## 6. 常见用途

- 参数化位宽的寄存器、计数器
- 批量例化同一模块
- 加法树、乘法树
- 多位 IO 缓冲
- 根据参数选择不同实现
- 生成 RAM/ROM 的多个 bank
- 生成流水线各级

---

## 7. 完整例子：参数化移位寄存器

```verilog
module shift_reg #(
    parameter WIDTH = 8,
    parameter DEPTH = 4
)(
    input  wire             clk,
    input  wire             rst_n,
    input  wire             din,
    output wire             dout
);

    reg [WIDTH-1:0] shift [0:DEPTH-1];

    genvar i;
    generate
        for (i = 0; i < DEPTH; i = i + 1) begin : gen_shift
            always @(posedge clk or negedge rst_n) begin
                if (!rst_n)
                    shift[i] <= {WIDTH{1'b0}};
                else if (i == 0)
                    shift[i] <= {shift[i][WIDTH-2:0], din};
                else
                    shift[i] <= shift[i-1];
            end
        end
    endgenerate

    assign dout = shift[DEPTH-1][WIDTH-1];

endmodule
```

这个例子用 `generate for` 批量生成多级移位寄存器。

---

## 8. 注意事项

1. **`generate` 不能写在 `always` 里**  
   它和 `always`、`assign` 同级。

2. **循环边界必须是常量**  
   ```verilog
   for (i = 0; i < N; i = i + 1)   // N 必须是 parameter/localparam/常量
   ```

3. **`begin` 块必须命名**  
   ```verilog
   begin : gen_ff
   ```
   否则层次化引用和调试不方便。

4. **`genvar` 只用于 generate for**  
   不能当普通变量赋值。

5. **`generate if/case` 条件必须是常量**  
   不能是运行时信号。

6. **generate 可综合**  
   但里面写的语句本身也必须可综合。

7. **不要和 always 里的 for 混用**  
   一个是结构复制，一个是过程循环。

---

## 9. 总结口诀

> **`generate` 是编译时生成硬件，不是运行时循环。**  
> **`generate for` 批量复制，`generate if/case` 按常量选择。**  
> **循环变量用 `genvar`，循环边界必须是常量。**  
> **`begin : 块名` 要命名，方便层次引用。**  
> **能例化模块、写 assign、写 always，不能放进 always 里。**  
> **和 always 里的 for 区别：一个复制结构，一个过程赋值。**

读 `generate` 时，先看它是 `for`、`if` 还是 `case`，再看循环边界或条件是不是常量，最后把它展开成多份硬件来理解。