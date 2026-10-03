# 2-Verilog 入门学习笔记

> **本文档按 20 章目录重新整理**，内容来自原《Verilog 入门学习笔记》，并保留与知识库其他文件的链接。
> 整理原则：
> 1. **原有内容一条不删**（只删除真正重复的段落，并在删除处或保留处标注"重点重复 ⇒ 见 X 章"）；
> 2. **凡是重复出现超过一次的知识点，说明它是重点**，统一用 `⭐【重点·重复】` 标记；
> 3. **不常用的知识用 `【不常用】` 标注**；
> 4. 原笔记 15～20 章只有空标题，已用知识库内其他文件（`05A_三八译码器Verilog实现.md`、`03B_仿真验证.md`、`03A_Verilog输入.md`、`01/02/03三天入门verilog速成.md`、`wire和reg的对比.md`、`always语句.md` 等）的素材补全，补全处标注 `【补全·来源：xxx】`。

## 目录

1. Verilog 开发目的
2. 模块结构
3. 端口、方向、位宽
4. wire / reg / logic
5. assign 组合逻辑
6. 按位、移位、拼接
7. always 组合与时序
8. 阻塞与非阻塞
9. if / case
10. 运算符与优先级
11. 数据类型与数字表示
12. 模块例化与参数化
13. generate / function / task
14. 常用组合电路
15. 常用时序电路：触发器、寄存器、计数器、移位、分频、边沿检测
16. 状态机
17. Testbench 仿真
18. 开发流程与约束
19. 可综合与不可综合
20. 常见错误与代码风格

---

# 1. Verilog 开发目的

你的类比方向对了一半：**C 语言是描述"让数字系统去执行的算法/软件逻辑"**，最终编译成 CPU 指令；而 **Verilog 是直接描述"数字系统本身怎么构成、怎么随时间变化"**，最终仿真或综合成电路。也就是说，C 是站在硬件之上写软件，Verilog 是写硬件。

## Verilog 的开发目的

Verilog 是硬件描述语言（HDL），主要目的有：

1. **描述数字电路**
   描述组合逻辑、时序逻辑、寄存器、状态机、存储器、总线等。

2. **仿真验证**
   写 testbench，给设计加时钟、复位、激励，观察输出是否正确。这部分像软件，但目的是验证硬件。

3. **RTL 设计**
   在寄存器传输级描述数据如何在寄存器之间流动，这是最常用的可综合代码风格。

4. **逻辑综合**
   工具把可综合的 Verilog 转成门级网表：与门、或门、加法器、MUX、D 触发器、连线等。

5. **FPGA/ASIC 实现**
   最终映射到 FPGA 的查找表、触发器、DSP、BRAM，或 ASIC 的标准单元上。

所以一句话：
**C 写的是 CPU 要执行的指令序列；Verilog 写的是数字电路的结构和行为。**

## 理解 Verilog 代码的关键思维

读 Verilog 时，不要按 C 的"逐行顺序执行"去理解，而要问：

- 这个 `module` 对应什么硬件模块？
- 端口是芯片引脚吗？方向、位宽是什么？
- `wire` 是连线，谁在驱动它？
- `reg` 不一定真是寄存器，要看它出现在哪种 `always` 里。
- `assign` 通常描述组合逻辑连线。
- `always @(posedge clk)` 通常描述时序逻辑，会生成触发器。
- `always @(*)` 通常描述组合逻辑。
- `<=` 非阻塞赋值常用于时序逻辑；`=` 阻塞赋值常用于组合逻辑。
- 多个 `always`、`assign`、模块实例化之间是**并行**的。
- `if/case` 往往综合成 MUX 或优先级逻辑。
- `for` 在可综合代码里通常不是"运行时循环"，而是展开成多份硬件。
- 位宽很重要，截断、扩展、拼接都对应真实硬件连线。

例如：

```verilog
module counter(
    input clk,
    input rst,
    output reg [7:0] q
);
    always @(posedge clk or posedge rst)
        if (rst)
            q <= 8'd0;
        else
            q <= q + 1'b1;
endmodule
```

这段不是"程序循环执行 q=q+1"，而是描述：

- 一个 8 位寄存器 `q`
- 一个加法器 `q+1`
- 一个复位选择逻辑
- 每个时钟上升沿，`q` 更新一次

它对应的是硬件：寄存器 + 加法器 + 复位 MUX。

## 和 C 的对比

| C 语言 | Verilog |
|---|---|
| 写软件算法 | 写数字硬件 |
| 编译成 CPU 指令 | 综合成电路网表 |
| 顺序执行 | 并行、事件驱动 |
| 函数是基本单位 | `module` 是基本单位 |
| 变量在内存/寄存器中 | `wire/reg` 映射连线/存储 |
| `for/while` 运行时循环 | `for` 常展开为硬件 |
| 结果是可执行文件 | 结果是仿真模型、网表、比特流 |

## 对你读代码的帮助

把 Verilog 代码当成"电路说明书"，而不是"程序流程"。
每读一段，就问：

1. 这是组合逻辑还是时序逻辑？
2. 信号由谁驱动？位宽多少？
3. 时钟边沿到来时哪些信号变化？
4. 复位时发生什么？
5. 综合出来大概是什么硬件：MUX、加法器、计数器、状态机、RAM？

这样你就能从"看语法"转向"看硬件"，Verilog 代码会容易理解得多。

> ⭐【重点·重复】本章出现的"`wire` 看驱动、`reg` 看 always""组合逻辑用 `=`、时序逻辑用 `<=`""多个 `always` 并行""`if/case` 综合成 MUX"，在后面的第 4、5、7、8、9 章会反复出现，是全篇的核心，务必记牢。
> 各章分工导航：模块结构 → 第 2 章；端口与三要素 → 第 3 章；`wire/reg/logic` → 第 4 章；`assign` → 第 5 章；`always` → 第 7 章；阻塞/非阻塞 → 第 8 章。

---

# 2. 模块结构

`module` 是 Verilog 的基本单位，相当于 C 的函数，但它是**电路说明书**：一个 `module` 就是一块硬件。

## 1. 模块定义框架

```Verilog
module 模块名([端口列表]);
[端口信号声明;]
[参数声明;]
```

## 2. 模块的定义

### [模块定义](模块的定义.md)

ANSI 风格与非 ANSI 风格（两种写法功能完全一样）：

两种写法**功能上完全一样**，就像 C 语言里两种函数定义风格：

- **ANSI 风格**（现代 C）：直接在参数列表里写类型和名字。
- **K&R 风格**（老式 C）：先写参数名，再在函数体前声明类型。

Verilog 也分成这两种：

| Verilog 写法 | 类比 C 语言 |
|---|---|
| `module mux2(input a, input b, input sel, output y);` | `void mux2(int a, int b, int sel, int *y) { ... }` |
| `module mux2(a, b, sel, y); input a, b, sel; output y;` | `void mux2(a, b, sel, y) int a; int b; int sel; int *y; { ... }` |

所以你的例子：

```verilog
module mux2(
    input  a,
    input  b,
    input  sel,
    output y
);
```

和

```verilog
module mux2(
     a, b, sel, y
);
input  a, b, sel;
output y;
```

**最终生成的模块接口一模一样**，综合和仿真结果也一样。
只是第一种更清晰、更现代，第二种是老式写法，类似 K&R C，已经过时。

### 用 C 语言类比端口列表

端口列表就像 C 函数的**参数列表**：

```c
void mux2(int a, int b, int sel, int *y) {
    *y = sel ? b : a;
}
```

- `input a` 像 C 的 `int a`：传进来的值，函数内部只读。
- `output y` 像 C 的 `int *y`：通过它把结果传出去。
- `inout` 像 C 的指针，既能读也能写。

在 Verilog 非 ANSI 风格里：

```verilog
module mux2(a, b, sel, y);
input a, b, sel;
output y;
```

就像 K&R C：

```c
void mux2(a, b, sel, y)
int a;
int b;
int sel;
int *y;
{
    *y = sel ? b : a;
}
```

先列出参数名，再在后面声明类型和方向。

### 注意：默认类型和方向，类似 C 的隐式规则

在 C 老标准里，如果不写类型，默认是 `int`，容易出错。
Verilog 非 ANSI 风格也有类似问题：

- 端口如果**没声明方向**，默认是 `inout`。
- 端口如果**没声明类型**，默认是 `wire`。

所以非 ANSI 风格容易漏写、写错。
ANSI 风格直接在端口列表里写清楚，像现代 C 要求每个参数都写类型，更安全。

### `wire` 和 `reg` 的 C 类比

- `wire` 像 C 里的**连线/引用**，必须由别的驱动源驱动，通常用 `assign`。
- `reg` 像 C 里的**变量**，可以在 `always` 过程块里赋值，能保存值。

如果输出要在 `always` 里赋值，必须声明成 `reg`：

ANSI 风格：

```verilog
output reg y;
```

非 ANSI 风格：

```verilog
output y;
reg y;
```

类比 C：你想在函数里修改一个值并保留，就需要一个真正的变量，而不是只读参数。

### 总结

- 两种写法功能等价，类似 C 的 ANSI 函数定义和 K&R 函数定义。
- 非 ANSI 风格先写端口名，再声明方向和类型，像老式 C。
- ANSI 风格直接在端口列表写清楚，像现代 C，推荐使用。
- 端口默认 `wire`，要过程赋值就加 `reg`。
- 以后写 Verilog，尽量用第一种 ANSI 风格。

## 3. 模块说明部分补充（来自三天速成笔记）

【补全·来源：`01三天入门verilog速成.md`】

### 模块名

- 指电路的名字，由用户指定
- **最好与文件名一致**（Quartus II 等 EDA 工具调试时需要）

### 端口列表

- 电路的输入输出信号名称列表，信号名由用户指定
- 各名称间用**逗号**隔开

### 端口方向声明

说明每个端口信号的属性：

- 方向：`input` / `output` / `inout`
- 数据类型：`wire` 或 `reg`
- 位宽：`[N1:N2]`

### 参数声明

说明参数的名称和数值。（详见第 12 章"模块例化与参数化"）

### 示例：全加器（Full Adder）的端口声明

```Verilog
module for(A, B, Cin, S, Cout);
    input  [3:0] A, B;
    input        Cin;
    output [3:0] S;
    output       Cout;
endmodule
```

- 位宽若不做说明，**默认为 1 位**
- 数据类型若不做说明，**默认为 wire 类型**

> ⭐【重点·重复】"位宽默认 1 位、数据类型默认 wire"在第 3 章（端口三要素）、第 4 章（wire/reg）、第 11 章（数据类型）都会再出现。这说明它是初学最容易踩的点。
> 端口、方向、位宽的完整讲解见第 3 章；`wire/reg/logic` 的选择见第 4 章。

---

# 3. 端口、方向、位宽

端口映射就是**模块实例化时，把外层信号连接到子模块端口上**（完整连接方法见第 12 章）。本章先讲端口本身的声明：声明一个端口（或任意信号）都要看**三要素**——方向、数据类型、位宽。

## 1. 端口列表是什么

[端口列表](端口.md)就是模块的"引脚列表"，写在模块名后面的括号里，用来[定义这个模块](模块的定义.md)和外部怎么连接。

```verilog
module mux2(
    input  a,
    input  b,
    input  sel,
    output y
);
    assign y = sel ? b : a;
endmodule
```

这里的 `(input a, input b, input sel, output y)` 就是端口列表。

端口列表描述了一个模块的**输入、输出、双向接口**，相当于==**芯片的引脚。**==

| 端口方向 | 含义 |
|---|---|
| `input` | 输入，外部信号进来 |
| `output` | 输出，模块信号出去 |
| `inout` | 双向，既能输入也能输出 |

例如 `mux2` 模块：

- `a`、`b` 是输入数据；
- `sel` 是选择信号；
- `y` 是输出结果。

当你在另一个模块里例化它时，就要把这些端口连起来：

```verilog
mux2 u_mux2(
    .a   (a),
    .b   (b),
    .sel (sel),
    .y   (y)
);
```

所以端口列表的作用是：**告诉上层模块，我这个模块有哪些引脚，分别怎么连接。**

## 2. 端口信号三要素

[端口信号声明](../FPGA设计竞赛/端口信号三要素.md)：声明一个端口或信号时的**三要素**：

```verilog
方向  数据类型  [位宽]  名字;
```

例如：

```verilog
input  wire [7:0] din;
output reg  [7:0] dout;
inout  wire [15:0] data_bus;
```

下面分别解释。

### 2.1 输入输出属性（方向）

表示这个信号是**从模块外面进来，还是从模块里面出去，还是双向**。

| 方向 | 含义 | 数电类比 | 能不能在模块内赋值 |
|---|---|---|---|
| `input` | 外部 → 模块 | 芯片输入引脚 | 不能，只能读 |
| `output` | 模块 → 外部 | 芯片输出引脚 | 可以，用 `assign` 或 `always` |
| `inout` | 双向 | 双向总线引脚 | 通常用三态门 |

例子：

```verilog
input  wire a;        // 输入，模块内部只能读
output wire y;        // 输出，用 assign 驱动
output reg  q;        // 输出，在 always 中赋值
inout  wire bus;      // 双向，必须用 wire
```

类比 C 语言：

- `input` 像函数参数，传进来只读。
- `output` 像返回值或指针参数，把结果送出去。
- `inout` 像双向指针，既能读也能写。

### 2.2 信号的数据类型

Verilog 里最常用两种：`wire` 和 `reg`。SystemVerilog 里还有 `logic`。（完整讲解见第 4 章）

**`wire`：导线**

- 对应数电里的**导线**。
- 必须由别的驱动源驱动，比如 `assign`、模块输出、门原语。
- 不能保存值，输入变，线上电平立刻变。
- 适合描述组合逻辑。

```verilog
wire y;
assign y = a & b;
```

数电类比：

```text
a ──┐
    ├──[与门]── y
b ──┘
```

**`reg`：过程赋值变量**

- 可以在 `always` 或 `initial` 里赋值。
- 名字叫 register，但**综合后不一定是寄存器**。
- 在 `always @(posedge clk)` 中赋值 → 通常综合成触发器。
- 在 `always @(*)` 中赋值 → 通常综合成组合逻辑。

```verilog
reg q;

always @(posedge clk) begin
    q <= d;          // 综合成 D 触发器
end
```

```verilog
reg y;

always @(*) begin
    y = a & b;       // 综合成与门，不是寄存器
end
```

**`logic`：SystemVerilog 的统一类型**

- 可以替代大部分 `wire` 和 `reg`。
- 新代码常用。

```verilog
logic [7:0] data;
```

**端口默认类型**

- `input` 和 `output` 默认是 `wire`。
- `inout` 必须是 `wire`。
- 如果 `output` 要在 `always` 中赋值，必须写成 `output reg` 或 `output logic`。

## [wire和reg对比](wire和reg的对比.md)

### 2.3 信号的位宽

位宽表示这个信号是**一根线还是一组总线**。

语法：

```verilog
[MSB:LSB] 名字;//Most Significant Bit：Least Significant Bit
```

例如：

```verilog
wire       a;        // 1 位
wire [7:0] data;     // 8 位，bit7 到 bit0
reg  [3:0] cnt;      // 4 位
input [15:0] addr;   // 16 位输入
```

数电类比：

- 1 位信号 = 一根导线。
- `[7:0]` = 8 根线组成的总线，类似 8 位数据总线。
- `[15:0]` = 16 位地址总线。

不写位宽时，默认是 **1 位**。

```verilog
input a;        // 等价于 input wire a;
input [7:0] b;  // 8 位
```

位宽决定能表示多少值：

| 位宽 | 范围（无符号） |
|---|---|
| 1 位 | 0 ~ 1 |
| 4 位 | 0 ~ 15 |
| 8 位 | 0 ~ 255 |
| 16 位 | 0 ~ 65535 |

类比 C：

```c
uint8_t  data;   // 类似 wire [7:0] data;
uint16_t addr;   // 类似 wire [15:0] addr;
```

> 位宽的本质（为什么十六进制/十进制写法最终都归到二进制位数、前导零也算位宽）见 [位宽本质.md](位宽本质.md)，以及第 11 章"数据类型与数字表示"。

### 2.4 三者组合起来看

```verilog
module example(
    input  wire        clk,       // 1 位输入导线
    input  wire        rst_n,     // 1 位输入导线
    input  wire [7:0]  din,       // 8 位输入总线
    output reg  [7:0]  dout,      // 8 位输出，在 always 中赋值
    output wire        ready,     // 1 位输出，用 assign 驱动
    inout  wire [15:0] data_bus   // 16 位双向三态总线
);

    reg  [3:0] cnt;               // 内部 4 位变量
    wire [3:0] sum;               // 内部 4 位连线

    assign sum = cnt + 1'b1;
    assign ready = (cnt == 4'd15);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            cnt <= 4'd0;
        else
            cnt <= cnt + 1'b1;
    end

    always @(posedge clk) begin
        dout <= din;
    end

endmodule
```

### 2.5 非 ANSI 风格里的默认规则

你之前问过这种写法：

```verilog
module mux2(a, b, sel, y);
input  a, b, sel;
output y;
```

这里：

- `a, b, sel, y` 默认都是 `wire`。
- 默认位宽都是 1 位。
- `input a, b, sel;` 表示三个 1 位输入。
- `output y;` 表示一个 1 位输出。

等价于 ANSI 风格：

```verilog
module mux2(
    input  wire a,
    input  wire b,
    input  wire sel,
    output wire y
);
```

如果 `y` 要在 `always` 中赋值，就要写成：

```verilog
output reg y;
```

或者非 ANSI 风格：

```verilog
output y;
reg y;
```

### 2.6 常见错误

1. **`output` 在 `always` 中赋值，却没声明 `reg`**

```verilog
output y;
always @(*) y = a & b;   // 错误，y 默认是 wire
```

正确：

```verilog
output reg y;
always @(*) y = a & b;
```

2. **把 `input` 声明成 `reg`**

```verilog
input reg a;   // 错误，输入不能是 reg
```

输入由外部驱动，模块内部只能读。

3. **`inout` 用 `reg`**

```verilog
inout reg bus;   // 错误
```

双向端口必须用 `wire` 或 `tri`，配合三态。

4. **位宽不匹配**

```verilog
wire [7:0] y;
wire [3:0] a;
assign y = a;   // 高位补零，容易出错
```

最好显式写：

```verilog
assign y = {4'b0, a};
```

5. **多驱动同一根 `wire`**

```verilog
assign y = a;
assign y = b;   // 冲突
```

数电里就像两个门输出直接短接，不允许。除非用三态。

### 2.7 总结

Verilog 里声明端口或信号，看三件事：

```text
方向  数据类型  [位宽]  名字
```

- **方向**：`input` / `output` / `inout`，决定信号往哪走。
- **数据类型**：`wire` 是导线，`reg` 是过程赋值变量，`logic` 是 SystemVerilog 统一类型。
- **位宽**：`[MSB:LSB]`，决定是 1 根线还是总线，不写默认 1 位。

用数电理解：

- 方向 = 芯片引脚方向。
- `wire` = 导线。
- `reg` = 可保存值的变量，综合后可能是触发器，也可能是组合逻辑。
- 位宽 = 总线宽度。

一句话：**端口和信号声明就是"方向 + 类型 + 位宽 + 名字"，和数电里的"引脚方向 + 导线/寄存器 + 总线宽度"对应。**

## 3. 为什么仿真的时候不用写端口列表

[仿真的时候不用写端口列表？](仿真时候不写端口列表的本质.md)

对，你的理解基本正确：**写不写端口列表，取决于这个模块有没有"对外引脚"需要和其他模块或外部世界连接。**

用 C 语言类比就是：

> **写不写参数列表，取决于这个函数需不需要从调用者接收数据、需不需要返回结果。**

### 3.1 有端口的模块 ≈ 有参数和返回值的函数

```verilog
module mux2(
    input  a,
    input  b,
    input  sel,
    output y
);
    assign y = sel ? b : a;
endmodule
```

类比 C：

```c
int mux2(int a, int b, int sel) {
    return sel ? b : a;
}
```

- `input a, b, sel` ≈ 函数参数，调用者把数据传进来。
- `output y` ≈ 返回值，模块把结果送出去。
- 别的模块例化它，就像调用函数并传参、接返回值。

```verilog
mux2 u_mux2(
    .a(a),
    .b(b),
    .sel(sel),
    .y(y)
);
```

类比：

```c
y = mux2(a, b, sel);
```

### 3.2 没有端口的模块 ≈ `void foo(void)` 函数

```verilog
module tb;
    reg a, b, sel;
    wire y;

    mux2 u_mux2(
        .a(a),
        .b(b),
        .sel(sel),
        .y(y)
    );
endmodule
```

类比 C：

```c
int main(void) {
    int a, b, sel, y;
    y = mux2(a, b, sel);
    return 0;
}
```

`main()` 不需要参数，也不需要返回值给谁，它是程序入口。
`tb` 也一样，它是仿真入口，不需要被别的模块连接，所以可以不写端口列表。

### 3.3 综合顶层模块 ≈ 必须暴露接口的库函数

```verilog
module top(
    input  wire clk,
    input  wire rst_n,
    input  wire [7:0] din,
    output wire [7:0] dout
);
    // ...
endmodule
```

类比 C：

```c
// 对外提供的 API，必须写清楚参数和返回值
void top(int clk, int rst_n, int din, int *dout) {
    // ...
}
```

FPGA 顶层模块要映射到芯片引脚，必须告诉工具：哪些引脚是输入，哪些是输出。
所以它必须有端口列表。

### 3.4 关键区别

| C 语言 | Verilog |
|---|---|
| 函数参数 | `input` 端口 |
| 函数返回值 / 指针参数 | `output` 端口 |
| 双向指针 | `inout` 端口 |
| `main()` 入口函数 | testbench 顶层，无端口 |
| 对外 API 函数 | FPGA 顶层模块，必须有端口 |
| 内部辅助函数 | 子模块，通常有端口，方便被例化连接 |
| `void foo(void)` | 无端口模块，只能作为顶层或完全自包含模块 |

| 场景 | 是否需要端口列表 | 原因 |
|---|---|---|
| 要被例化的子模块 | 必须写 | 上层需要通过端口连接它 |
| 综合到 FPGA 的顶层模块 | 必须写 | 需要映射到实际芯片引脚 |
| 仿真用的 testbench 顶层 | 通常不写 | 它是仿真根模块，没有上级连接，不综合成硬件 |
| 纯内部模块 | 可以没有端口 | 如果它只通过内部信号工作，不需要外部接口 |

### 3.5 但要注意一点

C 函数没有参数，还可以通过**全局变量**和外部交互。
Verilog 模块没有端口，原则上就**没有正规途径**和其他模块连接。

仿真时也许能用层次化引用强行访问内部信号：

```verilog
u_top.u_sub.signal = 1'b1;
```

但这就像 C 里到处用全局变量，**仿真可能能跑，综合通常不行，也不推荐**。

所以实际工程中：

- **要被例化的子模块**：必须有端口，否则上层没法连。
- **仿真顶层 testbench**：可以不写端口，因为它是根，不需要被连接。
- **综合顶层模块**：必须有端口，因为要对应 FPGA 引脚。
- **完全自包含、不与其他模块通信的模块**：可以没有端口，但很少见。

### 3.6 一句话总结

**端口列表就是模块的"函数参数 + 返回值"。**
需要和外部交换信号，就写端口；不需要被连接，只是仿真入口，就可以不写。
`module tb;` 就像 C 的 `main()`，而 `module top(input ...);` 就像对外提供的 API，必须写清楚接口。

> 补充：不是"仿真时不用写端口列表"，而是"**仿真顶层 testbench 不需要端口列表**，因为它不需要被连接，也不综合成实际电路"。如果你在仿真里写了一个子模块，比如 `mux2`，它仍然必须写端口列表，因为 testbench 要例化它、连接它。

> ⭐【重点·重复】"input 默认 wire、output 要么 wire 要么 reg、inout 必须 wire"在第 4、12 章还会出现，是端口相关的重复重点。

---

# 4. wire / reg / logic

## 1. 大方向对比

Q：wire 理解为导线本身不储存数值，reg 可以记录数值

你的理解**大方向对，但要加一句关键限定**：

> **wire 是"连线"，不存储；reg 是"过程赋值变量"，仿真中能保持值，但不一定综合成寄存器。**
> 在 Verilog 里，**reg ≠ register**，看到 `reg` 不要立刻认为它是触发器。

完整对照见 [wire和reg的对比.md](wire和reg的对比.md)。

### 对比表

| 项目 | wire | reg |
|---|---|---|
| 本质 | 线网 net，表示连接 | 变量 variable，过程赋值目标 |
| 赋值方式 | `assign`、模块端口、门原语 | `always` / `initial` 过程块 |
| 仿真行为 | 由驱动源决定，无驱动为 `z` | 保持最后一次过程赋值，未赋值常为 `x` |
| 是否存储 | 不存储 | 类型本身不保证，看综合上下文 |
| 综合结果 | 连线、组合逻辑输出 | 可能是组合逻辑，也可能是触发器/锁存器 |
| 典型端口 | `input` 默认是 wire | `output reg` 需过程赋值时用 |
| 多驱动 | 可多驱动，靠 net 解析 | 通常不允许 |
| 读代码时看 | 谁在驱动它 | 它在哪种 `always` 里 |

## 2. ⭐【重点·重复】关键：reg 综合成什么，取决于 always

这一条在后面第 7 章（always）、第 8 章（阻塞/非阻塞）、第 15 章（时序电路）会反复出现，是全篇最重要的判据。

### 2.1 wire + assign：组合逻辑连线

```verilog
wire y;
assign y = a & b;
```

`y` 是一根线，由与门输出驱动，输入一变，`y` 就变。

### 2.2 reg + always @(*)：还是组合逻辑

```verilog
reg y;
always @(*) begin
    y = a & b;
end
```

虽然写的是 `reg`，但综合出来通常还是与门，不是寄存器。
因为 `always @(*)` 对输入敏感，输入变了就重新计算。

### 2.3 reg + always @(posedge clk)：这才是触发器

```verilog
reg q;
always @(posedge clk) begin
    q <= d;
end
```

这个 `q` 才通常综合成 D 触发器，在时钟上升沿更新，并保持到下一个上升沿。

## 3. 所以更准确的说法是

- `wire`：**结构连线**，必须被驱动，不存储。
- `reg`：**过程赋值变量**，仿真中能保存值；硬件上可能是：
  - 组合逻辑输出；
  - 锁存器；
  - 触发器；
  - 取决于 `always` 的敏感列表和赋值是否完整。

## 4. 一个例子对比

```verilog
module demo(
    input clk,
    input a, b,
    output wire y,
    output reg z,
    output reg q
);

    assign y = a & b;          // wire：组合逻辑

    always @(*) begin
        z = a & b;             // reg：但综合成组合逻辑
    end

    always @(posedge clk) begin
        q <= a & b;            // reg：综合成触发器
    end

endmodule
```

这里：

- `y` 是 wire，组合输出；
- `z` 是 reg，但也是组合输出；
- `q` 是 reg，且是时序逻辑，通常对应触发器。

## 5. ⭐【重点·重复】何时用 wire，何时用 reg

最实用的判断法不是"它存不存储"，而是：

> **它在哪儿被赋值？谁在驱动它？**

Verilog-2001 里，语法规则其实很硬：

- `assign` 左边 → 必须是 `wire`
- `always` / `initial` 左边 → 必须是 `reg`
- 模块实例化输出、门原语输出、双向口 → 连 `wire`
- `output` 端口看内部怎么驱动：`assign` 驱动用 `output wire`，`always` 驱动用 `output reg`
- `input` 端口默认 `wire`
- `inout` 必须 `wire`

### 快速对照表

| 场景 | 用 wire 还是 reg |
|---|---|
| `assign y = a & b;` | `wire y;` |
| `always @(*) y = a & b;` | `reg y;` |
| `always @(posedge clk) q <= d;` | `reg q;` |
| 模块例化输出连接 | `wire out;` |
| 门原语输出 | `wire` |
| 双向端口 `inout` | `wire` |
| 测试平台里产生时钟、复位、激励 | `reg` |
| DUT 输出连到 testbench | `wire` |
| `output` 由 `assign` 驱动 | `output wire` |
| `output` 由 `always` 驱动 | `output reg` |

### 例子

**1. 组合逻辑两种写法**

用 `assign`：

```verilog
wire y;
assign y = a & b;
```

用 `always`：

```verilog
reg y;
always @(*) begin
    y = a & b;
end
```

虽然第二个写的是 `reg`，但综合出来通常还是组合逻辑，不是触发器。
因为它不在时钟边沿更新。

**2. 时序逻辑**

```verilog
reg q;
always @(posedge clk) begin
    q <= d;
end
```

这里 `q` 是 `reg`，通常综合成 D 触发器。

**3. 模块输出端口**

```verilog
module demo(
    input clk,
    input a,
    input b,
    output wire y,
    output reg q
);

    assign y = a & b;

    always @(posedge clk) begin
        q <= a & b;
    end

endmodule
```

- `y` 由 `assign` 驱动 → `output wire`
- `q` 由 `always` 驱动 → `output reg`

**4. 模块实例化**

```verilog
wire out;
sub u_sub(
    .out(out),
    .in(a)
);
```

模块输出是驱动源，所以连到 `wire`。

**5. Testbench**

```verilog
reg clk;
reg rst;
wire dout;

initial begin
    clk = 0;
    forever #5 clk = ~clk;
end

initial begin
    rst = 1;
    #20 rst = 0;
end

dut u_dut(
    .clk(clk),
    .rst(rst),
    .dout(dout)
);
```

- `clk`、`rst` 在 `initial/always` 里赋值 → `reg`
- `dout` 是 DUT 输出 → `wire`

### 常见错误

```verilog
wire y;
always @(*) y = a & b;   // 错：wire 不能出现在过程赋值左边

reg q;
assign q = a & b;        // 错：reg 不能用于连续赋值左边
```

## 6. SystemVerilog 里的 `logic`

SystemVerilog 引入了 `logic`，大部分场景可以替代 `wire` 和 `reg`：

```verilog
logic y;
assign y = a & b;        // 可以

logic q;
always @(posedge clk)
    q <= d;              // 可以
```

但注意：

- **多驱动**、双向总线仍然要用 `wire`。
- 单驱动时 `logic` 很方便，但不要因为用 `logic` 就忘了硬件本质。

## 7. 判断口诀

> **always 左值用 reg，assign 左值用 wire；**
> **模块输出连 wire，双向端口必须 wire；**
> **output 看驱动：assign 用 wire，always 用 reg；**
> **SystemVerilog 用 logic，多驱动还得 wire。**

所以，写代码时先问自己：

1. 这个信号在 `always/initial` 里被赋值吗？是 → `reg` / `logic`。
2. 它由 `assign`、模块输出、门原语驱动吗？是 → `wire`。
3. 它是端口吗？`input` → `wire`；`output` 看内部驱动；`inout` → `wire`。
4. 有多个驱动源吗？有 → `wire`。

记住：**`reg` 不等于寄存器，`wire` 不等于简单连线。关键看赋值方式和驱动来源。**

## 8. 补充：wire / reg 速查（来自三天速成笔记）

【补全·来源：`01三天入门verilog速成.md`】

| 类型 | 含义 | 赋值方式 | 备注 |
|------|------|---------|------|
| `wire` | 电路中的连线（线网类型） | 必须用 `assign` | 默认类型 |
| `reg` | 寄存器类型 | 必须用 `always` 块内过程赋值 | 需手动声明 |

> 如果要用 `always` 语句对信号赋值，必须先将其声明为 `reg` 类型。

## 9. 总结口诀

> **wire 看驱动，reg 看 always。**
> **wire 是线，reg 是过程变量；reg 不一定寄存器。**

读 Verilog 时，不要只盯着 `wire` 和 `reg` 这两个关键字，而要看：

1. 它在哪里被赋值？
2. 是连续赋值还是过程赋值？
3. 敏感列表是 `*` 还是 `posedge clk`？
4. 赋值完整不完整？
5. 综合出来是连线、组合逻辑，还是触发器？

这样就不会被 `reg` 这个名字误导。

---

# 5. assign 组合逻辑

`assign` 是 Verilog 里的**连续赋值语句**，用来给 `wire` 类型的信号持续驱动一个表达式。它描述的是**组合逻辑**：右边输入一变，左边输出立刻跟着变。用数电来理解 `assign` 见 [数电中的assign.md](数电中的assign.md)。

用 C 语言类比，`assign` 不像"调用一次函数"，而更像：

- **电子表格公式**：`Y = A & B`，A 或 B 一变，Y 自动重算。
- 或者 C 里的宏：`#define Y (SEL ? B : A)`，但它是硬件连线，一直生效。

## 1. 基本语法

```verilog
assign 目标 = 表达式;
```

例子：

```verilog
wire y;
assign y = a & b;
```

- 左边必须是 `wire` 或 `net` 类型。
- 右边可以是任意组合逻辑表达式。
- 不能写在 `always` 或 `initial` 里面。
- 不能用来给 `reg` 赋值。

类比 C：

```c
// 不是这种一次性赋值
y = a & b;

// 更像这种持续关系
#define Y (A & B)
```

但硬件里 `assign` 是并行、持续工作的，不是按顺序执行。

## 2. 常见用法

### 简单逻辑

```verilog
assign y = a & b;
assign z = a | b;
assign n = ~a;
```

类比 C 的位运算表达式：

```c
y = a & b;
```

但 Verilog 中这行会综合成与门，并且一直工作。

### 条件运算符，相当于多路器

```verilog
assign y = sel ? b : a;
```

类比 C：

```c
y = sel ? b : a;
```

综合出来是一个 2 选 1 多路器。

### 拼接

```verilog
assign y = {a, b};
assign y = {2{a}};   // 复制
```

类比 C 里把两个字节拼成一个字：

```c
y = (a << 8) | b;
```

（拼接的完整讲解见第 6 章）

### 位选

```verilog
assign y = data[7];
assign y = data[3:0];
```

类比 C：

```c
y = (data >> 7) & 1;
y = data & 0x0F;
```

### 加法器

```verilog
assign sum = a + b;
assign carry = (a + b) > 8'hFF;
```

类比 C：

```c
sum = a + b;
```

但 Verilog 中这会综合成加法器电路。

## 3. `assign` 和 `always @(*)` 的区别

⭐【重点·重复】这条对比在第 7 章（always）里会再次出现。

两者都能描述组合逻辑：

```verilog
// assign 写法
assign y = sel ? b : a;
```

```verilog
// always 写法
always @(*) begin
    if (sel)
        y = b;
    else
        y = a;
end
```

区别：

| 对比 | `assign` | `always @(*)` |
|---|---|---|
| 赋值目标 | `wire` | `reg` 或 `logic` |
| 赋值符号 | `=` | `=` 阻塞赋值 |
| 适合场景 | 简单表达式 | 复杂 `if/case/for` |
| 是否并行 | 是 | 是，但块内顺序执行 |
| 能否写多行 | 通常一行 | 可以多行 |

C 类比：

- `assign` 像直接写一个表达式或宏。
- `always @(*)` 像写一个函数体，里面可以用 `if`、`switch`、循环。

## 4. `assign` 和时序逻辑的区别

时序逻辑用 `always @(posedge clk)`：

```verilog
always @(posedge clk) begin
    q <= d;
end
```

类比 C：

```c
// 每个时钟周期执行一次
q = d;
```

而 `assign` 是组合逻辑，不等时钟：

```verilog
assign y = a & b;
```

类比 C：

```c
// 只要 a 或 b 变，y 立刻变
y = a & b;
```

区别在于：

- `assign` 没有时钟，输入变输出就变。
- `always @(posedge clk)` 要等时钟边沿才更新。
- `assign` 给 `wire` 赋值。
- 时序逻辑给 `reg` 赋值，用 `<=`。

## 5. 注意事项

### 左边必须是 `wire`

```verilog
wire y;
assign y = a & b;   // 正确
```

```verilog
reg y;
assign y = a & b;   // 错误
```

如果端口是 `output reg`，就不能用 `assign`。

### 不能多驱动

```verilog
assign y = a;
assign y = b;   // 冲突，两个驱动源
```

这相当于两个输出脚接在一起，可能短路。
除非用三态门，否则不要多驱动同一根 `wire`。

### 延迟不可综合

```verilog
assign #5 y = a & b;
```

`#5` 只用于仿真，FPGA 综合会忽略或报错。

### 不能写在 `always` 里

```verilog
always @(*) begin
    assign y = a & b;   // 错误
end
```

`assign` 是模块级语句，和 `always` 平级。

### 位宽要匹配

```verilog
wire [7:0] y;
assign y = a;   // a 只有 4 位，会补零或截断
```

最好显式写清楚：

```verilog
assign y = {4'b0, a};
```

## 6. 完整例子：2 选 1 多路器

```verilog
module mux2(
    input  wire a,
    input  wire b,
    input  wire sel,
    output wire y
);
    assign y = sel ? b : a;
endmodule
```

类比 C：

```c
int mux2(int a, int b, int sel) {
    return sel ? b : a;
}
```

但 Verilog 中 `assign` 不是调用一次，而是硬件一直连接着。

## 7. 用数电理解 assign

【补全·来源：`数电中的assign.md`】

### 7.1 数电里的"连线"就是 `wire`

在数电里，你画电路图时：

- 门电路的输出通过**导线**连到下一个门的输入。
- 这根导线上的电平由驱动它的那个输出决定。
- 导线本身不存储值，输入变，导线上的电平立刻变。

Verilog 里的 `wire` 就是这根**导线**：

```verilog
wire y;
```

`assign` 就是**声明这根导线接到哪个逻辑输出上**：

```verilog
assign y = a & b;
```

数电里你画的是：

```text
a ──┐
    ├──[与门]── y
b ──┘
```

Verilog 里写的是：

```verilog
assign y = a & b;
```

**两者完全对应。**

### 7.2 `assign` 对应的就是数电中的组合逻辑电路

数电中所有"输出只取决于当前输入、不含记忆元件"的电路，都是组合逻辑。
Verilog 中所有 `assign` 描述的都是组合逻辑。

| 数电电路 | Verilog `assign` |
|---|---|
| 与门 | `assign y = a & b;` |
| 或门 | `assign y = a \| b;` |
| 非门 | `assign y = ~a;` |
| 异或门 | `assign y = a ^ b;` |
| 与非门 | `assign y = ~(a & b);` |
| 数据选择器 | `assign y = sel ? b : a;` |
| 半加器 Sum | `assign sum = a ^ b;` |
| 半加器 Carry | `assign carry = a & b;` |
| 全加器 Sum | `assign sum = a ^ b ^ cin;` |
| 全加器 Carry | `assign cout = (a & b) \| (a & cin) \| (b & cin);` |
| 多位加法器 | `assign {cout, sum} = a + b + cin;` |

你数电里怎么画电路，Verilog 就怎么写 `assign`。一一对应。

### 7.3 `assign` 不是"执行一次"，而是"一直连着"

这是从软件思维转向硬件思维最关键的一点。

在数电里，你搭好一个与门电路，通上电之后：

- 只要 `a` 和 `b` 有变化，`y` 立刻跟着变。
- 它不需要"被调用"，它一直在工作。
- 它没有"执行顺序"，所有门同时工作。

`assign` 也是这样：

```verilog
assign y = a & b;
```

这不是"算一次 `a & b` 然后赋值给 `y`"。
这是"**把 `y` 这根导线接到一个与门的输出上**"。之后 `a`、`b` 只要变，`y` 就自动变。

类比数电：

> 你不是在"执行"与门，你是在"搭"与门。

### 7.4 和 `always @(posedge clk)` 的对比

数电里有两类基本电路：

| 类型 | 特点 | Verilog 写法 |
|---|---|---|
| 组合逻辑 | 无时钟，输入变输出立刻变 | `assign` 或 `always @(*)` |
| 时序逻辑 | 有时钟，只在时钟边沿更新 | `always @(posedge clk)` |

数电里：

- 组合逻辑：与门、或门、多路器、加法器、译码器。
- 时序逻辑：触发器、寄存器、计数器、状态机。

Verilog 里：

```verilog
// 组合逻辑：像数电里的门电路
assign y = a & b;

// 时序逻辑：像数电里的 D 触发器
always @(posedge clk) begin
    q <= d;
end
```

所以：

- `assign` 对应数电中的**组合逻辑电路**。
- `always @(posedge clk)` 对应数电中的**触发器/寄存器**。

### 7.5 `assign` 和"多驱动"问题

数电里，两根导线不能直接接在一起，否则可能短路。
如果你把两个门输出接在同一点，除非是**三态门**或**集电极开路**，否则会冲突。

Verilog 里也一样：

```verilog
assign y = a;
assign y = b;   // 错误：两个驱动源驱动同一根 wire
```

这就像数电里把两个普通门输出直接短接，不允许。

三态门在 Verilog 里可以这样写：

```verilog
assign y = en ? a : 1'bz;
```

`1'bz` 就是高阻态，对应数电里的**高阻**。

### 7.6 `assign` 和"总线"

数电里总线是多个信号共用一组导线，通过三态门或多路器选择谁来驱动。

Verilog 里：

```verilog
wire [7:0] bus;

assign bus = en1 ? data1 : 8'bz;
assign bus = en2 ? data2 : 8'bz;
```

只要 `en1` 和 `en2` 不同时有效，就不会冲突。
这就是数电里的三态总线。

### 7.7 完整对照例子：全加器

**数电里**

你画一个全加器：

- `sum = a ⊕ b ⊕ cin`
- `cout = (a·b) + (a·cin) + (b·cin)`

**Verilog 里**

```verilog
module full_adder(
    input  wire a,
    input  wire b,
    input  wire cin,
    output wire sum,
    output wire cout
);
    assign sum  = a ^ b ^ cin;
    assign cout = (a & b) | (a & cin) | (b & cin);
endmodule
```

**每一行 `assign` 都对应数电里的一个逻辑表达式或一块组合电路。**

### 7.8 数电理解总结

| 数电概念 | Verilog `assign` |
|---|---|
| 导线 | `wire` |
| 门电路输出接到导线 | `assign` |
| 组合逻辑表达式 | `assign` 右边表达式 |
| 输入变输出立刻变 | `assign` 持续生效 |
| 不需要时钟 | `assign` 无时钟 |
| 三态门/高阻 | `1'bz` |
| 多驱动冲突 | 多个 `assign` 驱动同一 `wire` |
| 与触发器对比 | `assign` 是组合，`always @(posedge clk)` 是时序 |

一句话：

> **`assign` 就是在 Verilog 里"画导线 + 接门电路"，描述的是数电中的组合逻辑。**

## 8. 补充：assign 的特点（来自三天速成笔记）

【补全·来源：`01三天入门verilog速成.md`】

**基本格式**：

```Verilog
assign <赋值目标> = <表达式>;
```

**示例**：

```Verilog
assign Y = A;
assign Y = A & B;
```

**特点**：

1. **始终处于激活状态**：只要表达式中任意操作数发生变化，立即重新计算并赋值
2. 对应的另一类语句是**过程赋值语句**（`always`）
3. **赋值目标必须是 `wire` 类型**

> `wire` 表示电路中的**连线**（导线），只要一端逻辑变化，传出去的信号会立即变化。`wire` 是默认类型，所以不写数据类型时自动就是 `wire`。

## 9. 一句话总结

**`assign` 是给 `wire` 持续赋值的连续赋值语句，用来描述组合逻辑。**
它像 C 里的表达式或电子表格公式：输入一变，输出立刻变；不能给 `reg` 赋值，不能写在 `always` 里，不能多驱动，也不能用可综合延迟。

---

# 6. 按位、移位、拼接

本章把三类"位级运算"放在一起讲：**按位运算**（对应位分别算）、**移位运算**（整体挪位）、**拼接运算**（把几组线捆成一束）。它们都不产生进位、基本不消耗逻辑门，是描述硬件连线的基本工具。

> ⭐【重点·重复】这三类运算符在第 10 章"运算符与优先级"里会再列一次总表。**重复出现说明它们是重点**，尤其是"一个 `&` 是按位、两个 `&&` 是逻辑"这条易错点，全篇出现多次。

## 第一部分：按位运算

在 Verilog 里，**按位运算**就是：把两个多位信号的**对应位分别做逻辑运算**，每一位独立计算，**不产生进位**。它直接对应硬件里一排并行的门电路。

### 1. 常用按位运算符

| 运算符 | 名称 | 例子 | 结果 |
|---|---|---|---|
| `~` | 按位取反 | `~4'b1010` | `4'b0101` |
| `&` | 按位与 | `4'b1010 & 4'b1100` | `4'b1000` |
| `\|` | 按位或 | `4'b1010 \| 4'b1100` | `4'b1110` |
| `^` | 按位异或 | `4'b1010 ^ 4'b1100` | `4'b0110` |
| `~^` 或 `^~` | 按位同或 | `4'b1010 ~^ 4'b1100` | `4'b1001` |

规则是：

```text
a:  1 0 1 0
b:  1 1 0 0
-----------
&:  1 0 0 0
|:  1 1 1 0
^:  0 1 1 0
~a: 0 1 0 1
```

每一位只看对应位，互不影响。

### 2. ⭐【重点·重复】按位运算 vs 逻辑运算

这是最容易混的地方（第 10 章还会重复一次）。

| 按位运算 | 逻辑运算 |
|---|---|
| `~` 按位取反 | `!` 逻辑非 |
| `&` 按位与 | `&&` 逻辑与 |
| `\|` 按位或 | `\|\|` 逻辑或 |
| 结果是多位 | 结果只有 1 位 |
| 每一位独立算 | 整体判断真假 |

例子：

```verilog
wire [3:0] a = 4'b1010;
wire [3:0] b = 4'b1100;

wire [3:0] y_and = a & b;   // 4'b1000，按位与
wire       y_and2 = a && b; // 1'b1，因为 a 和 b 都非零

wire [3:0] y_not = ~a;      // 4'b0101，按位取反
wire       y_not2 = !a;     // 1'b0，因为 a 非零
```

记忆：

> **一个 `&` 是按位，两个 `&&` 是逻辑。**
> **一个 `|` 是按位，两个 `||` 是逻辑。**
> **一个 `~` 是按位取反，一个 `!` 是逻辑非。**

### 3. 归约运算：把多位压成 1 位

归约运算也是按位运算的一种特殊形式，它对**一个操作数的所有位**做运算，最后得到 1 位。

| 运算符 | 名称 | 含义 |
|---|---|---|
| `&a` | 归约与 | 所有位都是 1，结果才为 1 |
| `~&a` | 归约与非 | 所有位都是 1，结果为 0，否则 1 |
| `\|a` | 归约或 | 只要有一位是 1，结果就是 1 |
| `~\|a` | 归约或非 | 只要有一位是 1，结果就是 0 |
| `^a` | 归约异或 | 1 的个数为奇数则 1，偶数则 0 |
| `~^a` 或 `^~a` | 归约同或 | 1 的个数为偶数则 1，奇数则 0 |

例子：

```verilog
wire [3:0] a = 4'b1010;

wire r_and = &a;   // 0，因为不是全 1
wire r_or  = |a;   // 1，因为有 1
wire r_xor = ^a;   // 0，因为 1 的个数是 2，偶数
```

`^a` 常用来做奇偶校验。

### 4. 按位运算对应什么硬件

比如：

```verilog
wire [3:0] y;
assign y = a & b;
```

综合出来就是 **4 个与门并行**：

```text
a[0] ---|&|---> y[0]
b[0] ---|

a[1] ---|&|---> y[1]
b[1] ---|

a[2] ---|&|---> y[2]
b[2] ---|

a[3] ---|&|---> y[3]
b[3] ---|
```

同理：

- `a | b` → 4 个或门
- `a ^ b` → 4 个异或门
- `~a` → 4 个非门
- `^a` → 异或树，输出 1 位

所以按位运算非常适合描述：

- 掩码操作
- 置位、清位、翻转位
- 奇偶校验
- CRC、加密
- 总线操作

### 5. 实际用法示例

**掩码：只保留低 4 位**

```verilog
wire [7:0] data;
wire [7:0] low4 = data & 8'h0F;
```

**置位：把第 0 位置 1**

```verilog
wire [7:0] data;
wire [7:0] set_bit0 = data | 8'h01;
```

**清位：把第 0 位清 0**

```verilog
wire [7:0] data;
wire [7:0] clear_bit0 = data & ~8'h01;
```

**翻转：把所有位取反**

```verilog
wire [7:0] data;
wire [7:0] flip = data ^ 8'hFF;
```

**判断某一位**

```verilog
if (data[3] & 1'b1) begin
    // data 的第 3 位是 1
end
```

更常见直接写：

```verilog
if (data[3]) begin
    // ...
end
```

### 6. 完整模块例子

```verilog
module bitwise_demo(
    input  wire [3:0] a,
    input  wire [3:0] b,
    output wire [3:0] y_and,
    output wire [3:0] y_or,
    output wire [3:0] y_xor,
    output wire [3:0] y_not,
    output wire       y_logic_and,
    output wire       y_reduce_xor
);

    assign y_and = a & b;        // 按位与
    assign y_or  = a | b;        // 按位或
    assign y_xor = a ^ b;        // 按位异或
    assign y_not = ~a;           // 按位取反

    assign y_logic_and = a && b; // 逻辑与，结果 1 位
    assign y_reduce_xor = ^a;    // 归约异或，结果 1 位

endmodule
```

如果 `a=4'b1010`，`b=4'b1100`，结果：

```text
y_and = 1000
y_or  = 1110
y_xor = 0110
y_not = 0101
y_logic_and = 1
y_reduce_xor = 0
```

### 7. 位宽注意事项

按位运算结果的位宽通常取两个操作数中**较大的位宽**。较短的操作数会扩展。

例如：

```verilog
wire [3:0] a = 4'b1010;
wire [7:0] b = 8'b00001100;
wire [7:0] y = a & b;
```

`a` 会先扩展成 `8'b00001010`，再和 `b` 按位与。

建议：

- 显式写位宽，避免隐式扩展导致错误。
- 有符号数要小心符号扩展。
- 赋值时如果结果位宽大于左边，会截断。

### 8. 按位运算总结口诀

> **按位运算：对应位算，互不影响，不产生进位。**
> **`& | ^ ~` 是按位，`&& || !` 是逻辑。**
> **`^a` 是归约异或，输出 1 位，可做奇偶校验。**
> **按位运算直接映射成并行门电路，是可综合的。**

如果你想深入某个运算符，比如异或、同或、移位，或者想看它们怎么综合成电路，可以继续问。

## 第二部分：移位运算

移位运算在 Verilog 里就是把一个多位信号的每一位，整体往左或往右移动若干位。它直接对应硬件里的**移位器**，常用于乘除 2 的幂、串并转换、位对齐、流水线等。

### 1. 三种基本移位

| 运算符 | 名称 | 含义 |
|---|---|---|
| `<<` | 逻辑左移 | 整体左移，低位补 0 |
| `>>` | 逻辑右移 | 整体右移，高位补 0 |
| `<<<` | 算术左移 | 和 `<<` 一样，左移补 0 |
| `>>>` | 算术右移 | 右移时高位补符号位 |

注意：**没有"算术左移"和逻辑左移的区别**，左移都是低位补 0。区别只在右移。

### 2. 逻辑移位

不管符号，空出来的位一律补 0。

```verilog
wire [3:0] a = 4'b1010;

wire [3:0] lshift = a << 1;  // 4'b0100，左移 1 位，低位补 0
wire [3:0] rshift = a >> 1;  // 4'b0101，右移 1 位，高位补 0
```

图示：

```text
a       = 1 0 1 0
a << 1  = 0 1 0 0   (最高位 1 被移出丢弃，最低位补 0)
a >> 1  = 0 1 0 1   (最低位 0 被移出丢弃，最高位补 0)
```

注意：`a << 1` 的结果是 4 位，所以 `1 0100` 的高位 `1` 被截掉了。
如果不想丢位，要先把位宽扩大：

```verilog
wire [4:0] wide = {1'b0, a} << 1;  // 5'b10100
```

### 3. 算术移位

算术右移时，高位补的是**符号位**，用来保持有符号数的正负号。

```verilog
reg signed [3:0] a = 4'b1010;  // 有符号数，表示 -6

wire signed [3:0] arith_r = a >>> 1;  // 4'b1101，即 -3
wire        [3:0] logic_r = a >>  1;  // 4'b0101，即 5
```

图示：

```text
a          = 1 0 1 0   (有符号，最高位 1 表示负数)
a >>> 1    = 1 1 0 1   (高位补符号位 1)
a >>  1    = 0 1 0 1   (高位补 0)
```

算术右移相当于**除以 2 并向下取整**：

```text
-6 >>> 1 = -3
-6 >>  1 = 5   (逻辑右移，把符号位丢了，结果变成正数)
```

算术左移 `<<<` 和逻辑左移 `<<` 行为完全一样，都是低位补 0。

### 4. 移位对应什么硬件

**左移 1 位**

```verilog
assign y = a << 1;
```

综合出来就是把每一位往前挪一根线：

```text
a[0] -> y[1]
a[1] -> y[2]
a[2] -> y[3]
a[3] -> 丢弃
y[0] = 0
```

**右移 1 位**

```text
a[1] -> y[0]
a[2] -> y[1]
a[3] -> y[2]
y[3] = 0
a[0] -> 丢弃
```

**移位量可变**

如果移位量是变量：

```verilog
assign y = a << shamt;
```

综合出来是一个 **桶形移位器**，用多级 MUX 实现，可以移 0 到 N 位。

### 5. 移位和乘除 2 的关系

无符号数：

```verilog
a << 1  等价于  a * 2
a << 2  等价于  a * 4
a >> 1  等价于  a / 2   (向下取整)
a >> 2  等价于  a / 4
```

有符号数：

```verilog
a >>> 1 等价于  a / 2   (对负数也是向下取整)
```

所以硬件里常用移位代替乘除 2 的幂，因为移位器比乘法器便宜得多。

例子：

```verilog
wire [7:0] a = 8'd5;
wire [7:0] x2 = a << 1;   // 10
wire [7:0] x4 = a << 2;   // 20
wire [7:0] d2 = a >> 1;   // 2
```

### 6. 拼接实现移位

⭐【重点·重复】移位也可以用拼接 `{}` 来写，更直观、更明确（拼接的完整语法见本部分第三部分）：

```verilog
wire [3:0] a;

wire [3:0] lshift = {a[2:0], 1'b0};      // 左移 1 位
wire [3:0] rshift = {1'b0, a[3:1]};      // 右移 1 位
wire [3:0] arith  = {a[3], a[3:1]};      // 算术右移 1 位
```

好处：

- 位宽、补位一目了然；
- 不会因为位宽扩展踩坑；
- 综合结果和 `<<`、`>>` 一样。

### 7. 循环移位

Verilog 本身没有循环移位运算符，但可以用拼接实现。

**循环左移 1 位**

```verilog
wire [3:0] a;
wire [3:0] rot_l = {a[2:0], a[3]};
```

```text
a       = 1 0 1 0
rot_l   = 0 1 0 1
```

**循环右移 1 位**

```verilog
wire [3:0] rot_r = {a[0], a[3:1]};
```

```text
a       = 1 0 1 0
rot_r   = 0 1 0 1
```

循环移位常用于 CRC、加密、旋转编码器解码等。

### 8. 位宽陷阱

这是移位里最容易出错的地方。

**陷阱 1：左移丢高位**

```verilog
wire [3:0] a = 4'b1010;
wire [3:0] y = a << 1;   // 4'b0100，最高位 1 丢了
```

**陷阱 2：结果位宽由左边决定**

```verilog
wire [3:0] a = 4'b1010;
wire [4:0] y = a << 1;   // 5'b10100，这次没丢
```

因为 `a << 1` 在上下文里被扩展成 5 位。

**陷阱 3：右移不会自动扩展左边**

```verilog
wire [3:0] a = 4'b1010;
wire [4:0] y = a >> 1;   // 5'b00101，高位补 0
```

**建议**

- 需要保留高位时，先扩展再移位：

```verilog
wire [7:0] a = 8'b1010_1010;
wire [8:0] y = {1'b0, a} << 1;
```

- 或直接用拼接，最清楚：

```verilog
wire [8:0] y = {a, 1'b0};
```

### 9. 完整例子

```verilog
module shift_demo(
    input  wire [3:0] a,
    input  wire [1:0] shamt,
    output wire [3:0] lshift,
    output wire [3:0] rshift,
    output wire [3:0] arith_r,
    output wire [3:0] rot_l,
    output wire [7:0] mul4
);

    assign lshift  = a << 1;              // 逻辑左移 1 位
    assign rshift  = a >> 1;              // 逻辑右移 1 位
    assign arith_r = $signed(a) >>> 1;    // 算术右移 1 位
    assign rot_l   = {a[2:0], a[3]};      // 循环左移 1 位
    assign mul4    = a << 2;              // 乘以 4，结果 8 位

endmodule
```

如果 `a = 4'b1010`：

```text
lshift  = 0100
rshift  = 0101
arith_r = 1101   (把 a 当有符号数 -6，右移得 -3)
rot_l   = 0101
mul4    = 00101000  (10 * 4 = 40)
```

### 10. 移位总结口诀

> **`<<` 左移，低位补 0，可能丢高位。**
> **`>>` 逻辑右移，高位补 0。**
> **`>>>` 算术右移，高位补符号位，保持正负号。**
> **没有算术左移，左移都是补 0。**
> **移位 = 乘除 2 的幂，硬件里比乘法器便宜。**
> **循环移位用拼接实现：`{a[2:0], a[3]}`。**
> **位宽要先想清楚，不然左移会丢高位。**

如果你愿意，我可以接着讲**移位寄存器**，比如串并转换、序列检测，那和移位运算关系很紧。（见第 15 章）

## 第三部分：拼接运算

拼接运算符 `{}` 是 Verilog 里非常常用的运算符，它的作用是把几个信号按顺序**拼成一个更宽的整体**。在硬件上，它基本不消耗逻辑门，只是把几组线按顺序连到一起，相当于重新排线。

一句话：

> **拼接就是"把几根线捆成一束"：左边的是高位，右边的是低位。**

### 1. 基本语法与位序

```verilog
wire [3:0] a = 4'b1010;
wire [1:0] b = 2'b11;
wire [5:0] c = {a, b};
```

结果：

```text
c = 6'b101011
```

位序是：

```text
{ a , b }
  ^   ^
 高位 低位

a[3] a[2] a[1] a[0] b[1] b[0]
 1    0    1    0    1    1
```

所以 `c[5:2]` 就是 `a`，`c[1:0]` 就是 `b`。

### 2. 位宽计算

拼接结果的位宽 = 所有部分位宽之和。

```verilog
wire [7:0] x;
wire [3:0] y;
wire [11:0] z = {x, y};   // 8 + 4 = 12 位
```

如果拼接结果赋值给更窄的变量，会截断；赋值给更宽的变量，会根据上下文扩展（但拼接本身不会自动扩展）。

```verilog
wire [3:0] a = 4'b1010;
wire [1:0] b = 2'b11;
wire [4:0] c = {a, b};    // 6 位结果赋给 5 位，最高位截断：c = 5'b01011
```

最好让左右位宽明确匹配，避免意外截断。

### 3. 复制拼接

用 `{N{表达式}}` 可以把同一个表达式重复 N 次。

```verilog
wire [3:0] a = 4'b1010;
wire [7:0] b = {2{a}};      // 8'b10101010
wire [11:0] c = {3{a}};     // 12'b101010101010
```

也可以复制一部分：

```verilog
wire [7:0] d = {2{a[1:0]}}; // 8'b10101010
```

复制次数 N 必须是常量，不能是变量。

### 4. 拼接作为左值：拆分信号

拼接不仅可以放在右边，也可以放在左边，用来把宽信号拆成几部分。

```verilog
wire [7:0] data;
wire [3:0] high;
wire [3:0] low;

assign {high, low} = data;
```

这等价于：

```verilog
assign high = data[7:4];
assign low  = data[3:0];
```

常用于把总线拆成字段，比如：

```verilog
wire [31:0] instr;
wire [6:0]  opcode;
wire [4:0]  rd;
wire [4:0]  rs1;
wire [4:0]  rs2;
wire [6:0]  funct7;

assign {funct7, rs2, rs1, rd, opcode} = instr;
```

注意左右位宽必须一致，否则会报错或截断。

### 5. 拼接与移位的关系

拼接可以非常直观地实现移位。

**左移 1 位**

```verilog
wire [3:0] a;
wire [3:0] lshift = {a[2:0], 1'b0};
```

**逻辑右移 1 位**

```verilog
wire [3:0] rshift = {1'b0, a[3:1]};
```

**算术右移 1 位**

```verilog
wire signed [3:0] a;
wire signed [3:0] arith = {a[3], a[3:1]};
```

**循环左移 1 位**

```verilog
wire [3:0] rot_l = {a[2:0], a[3]};
```

**循环右移 1 位**

```verilog
wire [3:0] rot_r = {a[0], a[3:1]};
```

这些写法比 `<<`、`>>` 更明确，位宽和补位一目了然。

### 6. 实际应用

**6.1 组合成更宽的总线**

```verilog
wire [7:0] byte0, byte1, byte2, byte3;
wire [31:0] word = {byte3, byte2, byte1, byte0};
```

**6.2 符号扩展**

把一个有符号数扩展成更宽的位宽：

```verilog
wire signed [7:0] a;
wire signed [15:0] a_ext = {{8{a[7]}}, a};
```

`{8{a[7]}}` 把符号位复制 8 次，放在高位。

**6.3 零扩展**

```verilog
wire [7:0] a;
wire [15:0] a_zext = {8'b0, a};
```

**6.4 串并转换**

把串行输入的位拼成并行数据：

```verilog
reg [7:0] shift;
always @(posedge clk) begin
    shift <= {shift[6:0], din};
end
```

**6.5 构造常量**

```verilog
wire [31:0] const = {16'hABCD, 16'h1234};
```

### 7. 注意事项

1. **常量最好指定位宽**
   ```verilog
   {a, 0}      // 0 默认 32 位，可能不是你想要的
   {a, 1'b0}   // 明确 1 位
   ```

2. **复制次数必须是常量**
   ```verilog
   {N{a}}      // N 必须是常量，不能是变量
   ```

3. **位宽要匹配**
   作为左值时，左右位宽必须一致；作为右值时，注意结果位宽和赋值目标的位宽。

4. **拼接不产生逻辑**
   综合出来通常只是连线，不消耗门电路。但拼接后参与运算可能会产生逻辑。

5. **可以嵌套**
   ```verilog
   {a, {b, c}, d}
   ```

### 8. 完整例子

```verilog
module concat_demo(
    input  wire [3:0] a,
    input  wire [3:0] b,
    input  wire [7:0] data,
    output wire [7:0] y_cat,
    output wire [3:0] y_high,
    output wire [3:0] y_low,
    output wire [3:0] y_rot_l,
    output wire [15:0] y_sign_ext
);

    // 基本拼接
    assign y_cat = {a, b};          // 8 位：a 在高 4 位，b 在低 4 位

    // 拆分
    assign {y_high, y_low} = data;  // 高 4 位给 y_high，低 4 位给 y_low

    // 循环左移
    assign y_rot_l = {a[2:0], a[3]};

    // 符号扩展：假设 a 是有符号数
    assign y_sign_ext = {{12{a[3]}}, a};

endmodule
```

如果 `a = 4'b1010`，`b = 4'b0011`：

```text
y_cat   = 8'b10100011
y_rot_l = 4'b0101
y_sign_ext = 16'b1111111111111010
```

### 9. 拼接总结口诀

> **`{}` 拼接：左高位，右低位，位宽相加。**
> **`{N{}}` 复制：重复 N 次，N 是常量。**
> **左边也能用：拆分宽信号。**
> **移位、扩展、串并转换，拼接都能干。**
> **常量指定位宽，位宽要匹配，不然会截断。**

拼接运算符和移位、按位运算一样，是 Verilog 描述硬件连线的基本工具。读代码时看到 `{}`，就想想它把哪些线按什么顺序捆在了一起。

### 10. 本章重点小结（重复即重点）

| 重复出现多次的知识点 | 为什么是重点 | 详见 |
|---|---|---|
| 一个 `&` 是按位、两个 `&&` 是逻辑 | 全篇出现 3 次以上，初学最高频混淆点 | 第 6、10 章 |
| 归约运算 `^a` 输出 1 位 | 按位章节与运算符总览都单列 | 第 6、10 章 |
| 拼接可替代移位、循环移位 | 移位与拼接两节互相引用 | 第 6 章两部分 |
| 位宽规则（较大者决定 / 移位看左边 / 拼接相加） | 按位、移位、拼接、运算符总览各讲一次 | 第 6、10 章 |
| 常量要指定位宽 | 拼接、移位、数字表示、运算符各讲一次 | 第 6、10、11 章 |

---

# 7. always 组合与时序

`always` 语句块是 Verilog 里描述**过程行为**的核心结构。它不像 C 语言那样"顺序执行一次"，而是描述：

> **在什么条件下，重复执行里面的一段赋值逻辑。**

理解 `always` 的关键是看两件事：

1. **敏感列表**：什么时候触发？
2. **赋值方式**：用 `=` 还是 `<=`？

这两点决定了它综合成什么硬件。

详见 [always语句.md](always语句.md)（该文件还有电赛/FPGA 竞赛角度的考点总结）。

## 1. always 的两种基本类型

### 1.1 组合逻辑：always @(*)

```verilog
always @(*) begin
    y = a & b;
end
```

含义：

- 只要 `a` 或 `b` 变化，就重新执行；
- 不依赖时钟；
- 综合成组合逻辑，通常是与门、MUX 等。

`@(*)` 表示"对所有被读取的信号敏感"。也可以写成 `@(a or b)`，但容易漏信号，推荐用 `@(*)`。

### 1.2 时序逻辑：always @(posedge clk)

```verilog
always @(posedge clk) begin
    q <= d;
end
```

含义：

- 只在 `clk` 上升沿执行；
- 其他时间保持旧值；
- 综合成触发器。

带异步复位：

```verilog
always @(posedge clk or posedge rst) begin
    if (rst)
        q <= 1'b0;
    else
        q <= d;
end
```

- `rst` 一拉高，立即清零；
- 否则在时钟上升沿更新。

## 2. 敏感列表

⭐【重点·重复】敏感列表写的是"**这个 always 块内部被读取/用到的信号**"，不是整个模块的全部输入。这条在第 9 章（if/case）和 always语句.md 里都会重复出现，是最容易踩的坑。

敏感列表决定 always 什么时候被触发。

| 敏感列表 | 含义 | 综合结果 |
|---|---|---|
| `@(*)` | 任何输入变化 | 组合逻辑 |
| `@(a or b)` | a 或 b 变化 | 组合逻辑 |
| `@(posedge clk)` | 时钟上升沿 | 触发器 |
| `@(negedge clk)` | 时钟下降沿 | 触发器 |
| `@(posedge clk or posedge rst)` | 时钟沿或复位沿 | 带异步复位触发器 |
| `@(posedge clk or negedge rst_n)` | 时钟沿或低有效复位 | 带异步复位触发器 |

注意：

- 组合逻辑里如果敏感列表漏了信号，仿真和综合会不一致。
- 所以组合逻辑一律用 `@(*)`。
- 不要写不带敏感列表的 `always begin ... end`，会造成无限循环仿真、综合报错。

## 3. ⭐【重点·重复】组合逻辑 always 的写法

```verilog
always @(*) begin
    case (sel)
        2'b00: y = a;
        2'b01: y = b;
        2'b10: y = c;
        default: y = 1'b0;
    endcase
end
```

对应硬件：一个 4 选 1 MUX。

### 必须注意：所有分支都要赋值

```verilog
// 危险写法
always @(*) begin
    if (en)
        y = a;
    // en 为 0 时 y 没有赋值
end
```

这会在仿真中保持旧值，综合出**锁存器 latch**。
通常不希望意外产生锁存器，所以要写全：

```verilog
always @(*) begin
    if (en)
        y = a;
    else
        y = 1'b0;
end
```

或者用 `default` 覆盖 case 的所有情况。

另一种防锁存器写法（先给默认值）：

```verilog
always @(*) begin
    y = 1'b0;
    if (en)
        y = a;
end
```

## 4. 时序逻辑 always 的写法

### 4.1 简单触发器

```verilog
always @(posedge clk) begin
    q <= d;
end
```

### 4.2 同步复位

```verilog
always @(posedge clk) begin
    if (rst)
        q <= 1'b0;
    else
        q <= d;
end
```

复位只在时钟沿生效。

### 4.3 异步复位

```verilog
always @(posedge clk or posedge rst) begin
    if (rst)
        q <= 1'b0;
    else
        q <= d;
end
```

复位一拉高立即生效，不依赖时钟。

### 4.4 低有效异步复位

```verilog
always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        q <= 1'b0;
    else
        q <= d;
end
```

`rst_n` 为 0 时复位。

### 4.5 带使能

```verilog
always @(posedge clk) begin
    if (en)
        q <= d;
end
```

当 `en` 为 0，`q` 保持旧值。
综合出来是带使能的触发器，不是锁存器，因为它在时钟边沿更新。

## 5. 时序逻辑里的 if / case

⭐【重点·重复】这一条在第 9 章会再讲一次。

时序逻辑里也可以用 `if`、`case`，但含义不同：

```verilog
always @(posedge clk) begin
    if (sel)
        q <= a;
    else
        q <= b;
end
```

综合出来是：

```text
MUX 选择 a 或 b  ->  D 触发器 -> q
```

也就是说：

- `if/case` 在时序逻辑里描述的是**下一个时钟沿要写入什么值**；
- 不写 `else`，`q` 保持旧值，仍然综合成触发器。

例子：计数器

```verilog
always @(posedge clk or posedge rst) begin
    if (rst)
        cnt <= 8'd0;
    else if (en)
        cnt <= cnt + 1'b1;
end
```

`en` 为 0 时，`cnt` 保持。

## 6. always 里能写什么

可以在 always 里写：

- `if / else`
- `case / endcase`
- `for` 循环（可综合，但会展开成硬件）
- `while`（一般不综合）
- 函数调用
- 任务 task 调用
- 阻塞/非阻塞赋值

不能写：

- 模块实例化
- `assign` 连续赋值
- `initial`（可以单独存在，但不放在 always 里）

## 7. for 循环在 always 里

```verilog
integer i;
always @(*) begin
    for (i = 0; i < 4; i = i + 1)
        y[i] = a[i] & b[i];
end
```

综合时循环会**展开**成 4 份硬件，不是运行时循环。

所以：

- 循环次数必须是常量；
- 展开后对应多份并行逻辑。

## 8. 多个 always 的关系

⭐【重点·重复】"多个 always 并行、一个 reg 只能在一个 always 里赋值"在第 20 章"常见错误"里还会重复。

多个 always 之间是**并行**的：

```verilog
always @(posedge clk)
    q1 <= d1;

always @(posedge clk)
    q2 <= d2;
```

这两个 always 同时工作，各自综合成触发器。
它们之间没有先后顺序，不能靠"谁先执行"来传值。

如果要在 always 之间传信号，用 wire 或 reg 连接，靠信号本身同步。

## 9. 三种 always 写法速记

【补全·来源：`always语句.md`】

```verilog
// 1. 时序逻辑（寄存器）
always @(posedge clk or negedge rst_n) begin
    reg_out <= ...;
end

// 2. 组合逻辑（组合电路）
always @(*) begin
    wire_out = ...;
end

// 3. 仿真专用（Testbench，不可综合，仅仿真）
always #10 clk = ~clk;
```

> 补充（always语句.md 的电赛角度）：同步复位（`always @(posedge clk)` 里判 `rst_n`）在 Gowin FPGA 上资源更优；异步复位（复位信号放进敏感列表）复位立刻生效，电赛常用。规则是——时序逻辑用非阻塞 `<=`，异步复位信号必须放进敏感列表，`posedge` 是上升沿、`negedge` 是下降沿。

---

# 8. 阻塞与非阻塞

这是 always 里最重要的一对概念。详见本笔记第 7 章第 3 节；[always语句.md](always语句.md) 也把它列为"重中之重"。

## 1. ⭐【重点·重复】阻塞赋值 `=`

```verilog
always @(*) begin
    a = b;
    c = a;
end
```

执行顺序：

1. 先把 `b` 赋给 `a`；
2. 再把新的 `a` 赋给 `c`。

所以 `c` 最终等于 `b`。像 C 语言一样，逐行立即生效。

用途：

- **组合逻辑**中一般用 `=`。

## 2. ⭐【重点·重复】非阻塞赋值 `<=`

```verilog
always @(posedge clk) begin
    a <= b;
    c <= a;
end
```

执行顺序：

1. 先计算所有右边表达式的值；
2. 在时间步结束时同时更新左边。

所以：

- `a` 拿到的是**旧的 `b`**；
- `c` 拿到的是**旧的 `a`**；
- 两个赋值同时发生。

用途：

- **时序逻辑**中一般用 `<=`。

## 3. 对比表

【补全·来源：`always语句.md`】

| 类型 | 赋值符号 | 使用场景 | 硬件行为 |
|---|---|---|---|
| 阻塞赋值 | `=` | **组合逻辑 `always @(*)`** | 立即生效，顺序执行，阻塞后面语句 |
| 非阻塞赋值 | `<=` | **时序逻辑 `always @(posedge clk)`** | 块结束后统一更新，并行，模拟寄存器 |

## 4. 口诀

> **组合逻辑用 `=`，时序逻辑用 `<=`。**
> **不要在同一个 always 里混用两种赋值。**

一句话：**时序用 `<=`，组合用 `=`，千万别混用！**

## 5. 为什么非阻塞能"打拍"

非阻塞赋值"同时更新"的特性正好模拟了触发器的行为：所有触发器在同一个时钟沿采样**旧值**、输出**新值**，所以两级触发器级联时数据会一拍一拍往后传（见第 15 章的移位/流水线例子）。

错误示例（竞赛常错）：

```verilog
always @(posedge clk) begin
    a = b; // ❌ 时序块内使用阻塞赋值，仿真与综合不一致
end
```

> 【不常用】`=` 与 `<=` 在同一个 always 里彻底不混用是硬规则；而"在一个时序 always 里，用阻塞赋值只做临时变量计算、最后再非阻塞输出"这种写法在高级代码里偶尔出现，初学阶段不要用。

---

# 9. if / case

`if` 和 `case` 都是**行为级描述**，必须写在 `always` 或 `initial` 过程块里。它们描述的是硬件根据条件选择不同路径，综合出来通常是 **MUX、优先级选择逻辑、触发器使能、复位逻辑**，而不是软件里的"分支跳转"。

## 第一部分：if 语句

一句话：

> **`if` 描述"条件成立时做什么，不成立时做什么"，硬件上就是选择器或使能逻辑。**

### 1. 基本语法

```verilog
if (条件)
    语句1;
else
    语句2;
```

多行用 `begin ... end`：

```verilog
if (条件) begin
    // 多条语句
end else begin
    // 多条语句
end
```

`if` 只能出现在：

- `always` 块
- `initial` 块
- `function` / `task`
- `generate` 块（生成语句）

不能直接写在模块顶层。

### 2. 组合逻辑中的 if

```verilog
always @(*) begin
    if (sel)
        y = a;
    else
        y = b;
end
```

综合结果：一个 2 选 1 MUX。

```text
sel=0 -> y=b
sel=1 -> y=a
```

硬件：

```text
a ──┐
    ├── MUX ──> y
b ──┘
sel ──┘
```

**⭐【重点·重复】关键：组合逻辑里 if 必须写全**

```verilog
always @(*) begin
    if (en)
        y = a;
    // 没有 else
end
```

当 `en=0` 时，`y` 没有被赋值，仿真中保持旧值，综合出 **锁存器 latch**。
通常不希望意外锁存器，所以：

```verilog
always @(*) begin
    if (en)
        y = a;
    else
        y = 1'b0;
end
```

或者先给默认值：

```verilog
always @(*) begin
    y = 1'b0;
    if (en)
        y = a;
end
```

（这条"分支不全出锁存器"在第 7 章组合逻辑、第 9 章 case、第 20 章常见错误里都会重复，是电赛高频扣分点。）

### 3. 时序逻辑中的 if

```verilog
always @(posedge clk) begin
    if (en)
        q <= d;
end
```

综合结果：**带使能的 D 触发器**。

- `en=1`：时钟上升沿，`q` 更新为 `d`；
- `en=0`：时钟上升沿，`q` 保持旧值。

这里不写 `else` 是正常的，综合出的是触发器，不是锁存器。

**同步复位**

```verilog
always @(posedge clk) begin
    if (rst)
        q <= 1'b0;
    else
        q <= d;
end
```

- `rst` 只在时钟上升沿被检查；
- 复位与时钟同步。

**异步复位**

```verilog
always @(posedge clk or posedge rst) begin
    if (rst)
        q <= 1'b0;
    else
        q <= d;
end
```

- `rst` 一拉高立即复位；
- 不依赖时钟。

低有效异步复位：

```verilog
always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        q <= 1'b0;
    else
        q <= d;
end
```

### 4. if-else if 的优先级

```verilog
always @(*) begin
    if (sel0)
        y = a;
    else if (sel1)
        y = b;
    else if (sel2)
        y = c;
    else
        y = d;
end
```

综合出来是**优先级 MUX 链**：

- `sel0` 优先级最高；
- 如果 `sel0=1`，不管 `sel1`、`sel2` 是什么，都选 `a`；
- 否则再看 `sel1`，以此类推。

硬件上不是完全并行的多路选择器，而是带优先级的串行选择逻辑。

如果确实需要并行选择，用 `case` 更合适。

### 5. 嵌套 if

```verilog
always @(*) begin
    if (a) begin
        if (b)
            y = 1'b1;
        else
            y = 1'b0;
    end else begin
        y = c;
    end
end
```

综合成多层 MUX。
嵌套不要太深，否则组合逻辑路径变长，影响时序。

### 6. if 中的条件

条件可以是任意表达式：

```verilog
if (a)                 // a 非零为真
if (a == 1'b1)         // 推荐显式
if (a && b)            // 逻辑与
if (a & b)             // 按位与，结果非零为真
if (cnt == 8'd255)     // 比较
if (state == IDLE)     // 状态机
```

注意：

- `if (a)` 和 `if (a == 1'b1)` 在 `a` 是 1 位时等价；
- 多位的 `if (a)` 是判断 `a` 是否非零；
- 条件里出现 `x` 或 `z`，仿真中可能按假处理，但实际硬件不确定，应避免。

### 7. 常见错误（if）

**7.1 在 always 外写 if**

```verilog
if (a)
    y = b;   // 错，必须在 always/initial 里
```

**7.2 组合逻辑分支不全**

```verilog
always @(*) begin
    if (en)
        y = a;   // 缺少 else，产生锁存器
end
```

**7.3 时序逻辑用阻塞赋值**

```verilog
always @(posedge clk) begin
    if (en)
        q = d;   // 不推荐，应该用 <=
end
```

**7.4 混用 = 和 <=**

```verilog
always @(posedge clk) begin
    if (en)
        q <= d;
    else
        q = 1'b0;   // 错，同一 always 不要混用
end
```

**7.5 条件表达式位宽混乱**

```verilog
if (a == 4'd10)   // 明确位宽
```

**7.6 敏感列表漏信号**

```verilog
always @(a) begin
    if (b)
        y = a;   // b 变化不会触发
end
```

组合逻辑一律用 `@(*)`。

### 8. 完整例子（if）

```verilog
module if_demo(
    input  wire       clk,
    input  wire       rst_n,
    input  wire       en,
    input  wire       sel,
    input  wire [7:0] a,
    input  wire [7:0] b,
    output reg  [7:0] y_comb,
    output reg  [7:0] q
);

    // 组合逻辑：2 选 1 MUX
    always @(*) begin
        if (sel)
            y_comb = a;
        else
            y_comb = b;
    end

    // 时序逻辑：带使能、低有效异步复位的寄存器
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            q <= 8'd0;
        else if (en)
            q <= a;
        // en=0 时保持
    end

endmodule
```

### 9. if 总结口诀

> **`if` 只能写在过程块里，描述条件选择。**
> **组合逻辑用 `@(*)` + `=`，分支必须写全，否则出锁存器。**
> **时序逻辑用 `@(posedge clk)` + `<=`，不写 else 是保持，综合成触发器。**
> **`if-else if` 有优先级，综合成优先级 MUX 链。**
> **多分支选择用 `case` 更清晰。**
> **异步复位放敏感列表，同步复位放 `if` 里。**
> **一个 `always` 里不要混用 `=` 和 `<=`。**

读 `if` 时先看它在哪种 `always` 里，再看分支是否完整，就能判断它综合成 MUX、优先级逻辑还是触发器。

## 第二部分：case 语句

`case` 语句是 Verilog 里描述**多路分支选择**的过程语句，必须写在 `always` 或 `initial` 里。它通常综合成 **多路选择器 MUX**，也常用于状态机、指令译码、ALU 选择等。

一句话：

> **`case` 就是"看某个表达式的值，等于哪个常量，就执行哪条分支"。**

### 1. 基本语法

```verilog
case (表达式)
    值1: 语句1;
    值2: begin
        // 多条语句
    end
    值3: 语句3;
    default: 语句4;
endcase
```

例子：

```verilog
always @(*) begin
    case (sel)
        2'b00: y = a;
        2'b01: y = b;
        2'b10: y = c;
        default: y = d;
    endcase
end
```

综合结果：一个 4 选 1 MUX。

```text
sel=00 -> y=a
sel=01 -> y=b
sel=10 -> y=c
其他   -> y=d
```

### 2. 组合逻辑中的 case

组合逻辑用 `always @(*)` + 阻塞赋值 `=`。

```verilog
always @(*) begin
    case (sel)
        2'b00: y = a;
        2'b01: y = b;
        2'b10: y = c;
        default: y = d;
    endcase
end
```

**⭐【重点·重复】关键：分支必须写全，或者写 default**

```verilog
always @(*) begin
    case (sel)
        2'b00: y = a;
        2'b01: y = b;
        // 没有 default
    endcase
end
```

当 `sel` 为 `2'b10` 或 `2'b11` 时，`y` 没有被赋值，仿真中保持旧值，综合出 **锁存器 latch**。
通常不希望意外锁存器，所以：

- 要么列出所有情况；
- 要么加 `default`；
- 要么在 `case` 前给默认值：

```verilog
always @(*) begin
    y = 1'b0;
    case (sel)
        2'b00: y = a;
        2'b01: y = b;
    endcase
end
```

### 3. 时序逻辑中的 case

时序逻辑用 `always @(posedge clk)` + 非阻塞赋值 `<=`。

```verilog
always @(posedge clk) begin
    case (state)
        IDLE: state <= RUN;
        RUN:  state <= DONE;
        DONE: state <= IDLE;
        default: state <= IDLE;
    endcase
end
```

这里不写 `default` 也可以，但推荐写。
时序逻辑里，未覆盖的情况表示"保持旧值"，综合成触发器，不是锁存器。

带异步复位：

```verilog
always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        state <= IDLE;
    else begin
        case (state)
            IDLE: if (start) state <= RUN;
            RUN:  if (done)  state <= DONE;
            DONE: state <= IDLE;
            default: state <= IDLE;
        endcase
    end
end
```

### 4. casez 和 casex

普通 `case` 要求精确匹配。
`casez` 和 `casex` 允许某些位"不关心"。

| 语句 | 通配符 | 说明 |
|---|---|---|
| `case` | 无 | 精确匹配 |
| `casez` | `z`、`?` | 这些位不参与比较 |
| `casex` | `x`、`z`、`?` | 这些位不参与比较 |

例子：

```verilog
casez (instr)
    8'b1???_????: y = 1'b1;   // 最高位是 1
    8'b01??_????: y = 1'b0;   // 高两位是 01
    default:      y = 1'b0;
endcase
```

注意：

- `casez` 可综合，常用于指令译码；
- `casex` 有风险，仿真和综合可能不一致，一般不推荐；
- `?` 在 `casez` 和 `casex` 里都表示不关心。

### 5. case 与 if 的对比

⭐【重点·重复】if 与 case 的对比表在原笔记的 if 章节与 case 章节各出现一次，此处合并为一张。

| 项目 | `case` | `if-else if` |
|---|---|---|
| 优先级 | 通常并行匹配 | 有优先级 |
| 可读性 | 多分支清晰 | 少量分支清晰 |
| 综合结果 | 多路选择器 | 优先级 MUX 链 |
| 默认分支 | `default` | `else` |
| 锁存器风险 | 分支不全 | 分支不全 |
| 典型用途 | 状态机、译码、ALU | 简单条件、复位、使能 |

多分支选择优先用 `case`，条件少或带优先级时用 `if`。

### 6. case 综合成什么硬件

**6.1 并行多路选择器**

```verilog
always @(*) begin
    case (sel)
        2'b00: y = a;
        2'b01: y = b;
        2'b10: y = c;
        2'b11: y = d;
    endcase
end
```

综合成 4 选 1 MUX。

**6.2 优先级逻辑**

如果 `case` 项有重叠，第一个匹配优先，可能综合成优先级逻辑。
但可综合代码里，`case` 项通常应互斥。

**6.3 状态机**

```verilog
case (state)
    IDLE: ...
    RUN:  ...
    DONE: ...
endcase
```

综合成状态译码 + 下一状态逻辑。

### 7. 完整例子：ALU

```verilog
module alu(
    input  wire [3:0] op,
    input  wire [7:0] a,
    input  wire [7:0] b,
    output reg  [7:0] y
);

    always @(*) begin
        case (op)
            4'b0000: y = a + b;
            4'b0001: y = a - b;
            4'b0010: y = a & b;
            4'b0011: y = a | b;
            4'b0100: y = a ^ b;
            4'b0101: y = ~a;
            default: y = 8'b0;
        endcase
    end

endmodule
```

`op` 选择不同运算，综合成多路选择器加运算单元。

### 8. 完整例子：状态机

```verilog
module fsm(
    input  wire clk,
    input  wire rst_n,
    input  wire start,
    input  wire done,
    output reg  busy
);

    localparam IDLE = 2'b00;
    localparam RUN  = 2'b01;
    localparam DONE = 2'b10;

    reg [1:0] state, next_state;

    // 状态寄存器
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= IDLE;
        else
            state <= next_state;
    end

    // 下一状态组合逻辑
    always @(*) begin
        case (state)
            IDLE: next_state = start ? RUN : IDLE;
            RUN:  next_state = done  ? DONE : RUN;
            DONE: next_state = IDLE;
            default: next_state = IDLE;
        endcase
    end

    // 输出逻辑
    always @(*) begin
        case (state)
            IDLE: busy = 1'b0;
            RUN:  busy = 1'b1;
            DONE: busy = 1'b0;
            default: busy = 1'b0;
        endcase
    end

endmodule
```

（状态机的完整写法与三段式见第 16 章）

### 9. 常见错误（case）

**9.1 组合逻辑缺少 default**

```verilog
always @(*) begin
    case (sel)
        2'b00: y = a;
        2'b01: y = b;
    endcase
end
```

会综合出锁存器。

**9.2 在 always 外写 case**

```verilog
case (sel)   // 错，必须放在 always/initial 里
```

**9.3 混用 = 和 <=**

```verilog
always @(posedge clk) begin
    case (sel)
        1'b0: q <= a;
        1'b1: q = b;   // 错，不要混用
    endcase
end
```

**9.4 分支重复**

```verilog
case (sel)
    2'b00: y = a;
    2'b00: y = b;   // 重复，第一个优先，容易出错
endcase
```

**9.5 位宽不匹配**

```verilog
case (sel)       // sel 是 2 位
    0: y = a;    // 0 默认 32 位，可能匹配异常
    1: y = b;
endcase
```

应写成：

```verilog
2'b00: y = a;
2'b01: y = b;
```

**9.6 忘记 endcase**

```verilog
case (sel)
    2'b00: y = a;
// 缺少 endcase
```

### 10. case 总结口诀

> **`case` 写在过程块，多路分支选一个。**
> **组合逻辑用 `@(*)` + `=`，分支不全出锁存器。**
> **时序逻辑用 `@(posedge clk)` + `<=`，不写 default 是保持。**
> **精确匹配用 `case`，带通配用 `casez`。**
> **`casex` 有风险，一般不用。**
> **多分支用 `case`，少分支带优先级用 `if`。**
> **分支常量位宽要匹配，default 最好别省略。**

读 `case` 时先看它在哪种 `always` 里，再看分支是否完整，就能判断它综合成 MUX、优先级逻辑还是状态机。

---

# 10. 运算符与优先级

Verilog 的运算符很多，按功能可以分为十大类。最容易出错的是**优先级**和**位宽**，所以这一章先分类列出，再给完整优先级表，最后讲常见陷阱。

> ⭐【重点·重复】**按位、移位、拼接三类运算符的完整讲解在第 6 章**（按位运算、移位运算、拼接运算）。本章第 4～7 节是它们在"运算符总览"角度下的**精简重复版**，重复出现说明它们是重点；细节、硬件对应、陷阱与实际用例请回第 6 章。
> 算术语义与关系/相等/逻辑运算符只在运算符总览之外没有单独章节讲，本章是它们的**唯一详细出处**，不重复。

## 第一部分：运算符分类总览

## 1. 运算符分类总览

| 类别 | 运算符 | 说明 |
|---|---|---|
| 算术 | `+ - * / % **` | 加减乘除、取模、幂 |
| 关系 | `< <= > >=` | 比较大小，结果 1 位 |
| 相等 | `== != === !==` | 相等比较，结果 1 位 |
| 逻辑 | `&& \|\| !` | 逻辑与或非，结果 1 位 |
| 按位 | `~ & \| ^ ~^ ^~` | 对应位运算，结果多位 |
| 归约 | `& ~& \| ~\| ^ ~^ ^~` | 多位压成 1 位 |
| 移位 | `<< >> <<< >>>` | 左移、逻辑右移、算术右移 |
| 拼接 | `{ } {N{ }}` | 拼接、复制 |
| 条件 | `?:` | 三目运算符，相当于 MUX |
| 赋值 | `= <= += -=` 等 | 过程赋值、连续赋值 |

另外还有：

- 位选：`a[3]`、`a[3:0]`
- 成员：`mem[0]`、`mem[0][3]`
- 一元：`+ - ! ~ & ~& | ~| ^ ~^ ^~`
- 系统函数：`$signed`、`$unsigned`、`$clog2`、`$bits`

## 2. 算术运算符

| 运算符 | 名称 | 例子 | 结果 |
|---|---|---|---|
| `+` | 加 | `a + b` | 和 |
| `-` | 减 | `a - b` | 差 |
| `*` | 乘 | `a * b` | 积 |
| `/` | 除 | `a / b` | 商，整数除法 |
| `%` | 取模 | `a % b` | 余数 |
| `**` | 幂 | `a ** b` | a 的 b 次方 |

注意：

- `/` 是整数除法，`7 / 2 = 3`，不是 3.5；
- `%` 结果符号跟被除数，`-7 % 2 = -1`；
- `**` 一般不可综合，慎用；
- 综合里 `*`、`/`、`%` 会生成乘法器/除法器，面积大，能用移位代替就代替。

例子：

```verilog
wire [7:0] a = 8'd10;
wire [7:0] b = 8'd3;
wire [7:0] sum  = a + b;   // 13
wire [7:0] diff = a - b;   // 7
wire [7:0] prod = a * b;   // 30
wire [7:0] quot = a / b;   // 3
wire [7:0] rem  = a % b;   // 1
```

## 3. 关系运算符

| 运算符 | 名称 | 例子 | 结果 |
|---|---|---|---|
| `<` | 小于 | `a < b` | 1 位 |
| `<=` | 小于等于 | `a <= b` | 1 位 |
| `>` | 大于 | `a > b` | 1 位 |
| `>=` | 大于等于 | `a >= b` | 1 位 |

结果只有 1 位：真为 `1`，假为 `0`。

```verilog
wire gt = a > b;   // 1 位
```

注意：`<=` 在过程赋值里是非阻塞赋值，在表达式里是比较。看上下文区分。

```verilog
assign y = (a <= b);    // 比较
always @(posedge clk)
    q <= d;             // 非阻塞赋值
```

## 4. ⭐【重点·重复】按位运算符（详见第 6 章）

| 运算符 | 名称 | 例子 | 结果 |
|---|---|---|---|
| `~` | 按位取反 | `~4'b1010` | `4'b0101` |
| `&` | 按位与 | `4'b1010 & 4'b1100` | `4'b1000` |
| `\|` | 按位或 | `4'b1010 \| 4'b1100` | `4'b1110` |
| `^` | 按位异或 | `4'b1010 ^ 4'b1100` | `4'b0110` |
| `~^` 或 `^~` | 按位同或 | `4'b1010 ~^ 4'b1100` | `4'b1001` |

对应硬件：一排并行门电路。

## 5. ⭐【重点·重复】归约运算符（详见第 6 章）

归约运算符是**一元**的，对一个操作数的所有位做运算，结果 1 位。

| 运算符 | 名称 | 含义 |
|---|---|---|
| `&a` | 归约与 | 所有位都是 1 才为 1 |
| `~&a` | 归约与非 | 所有位都是 1 才为 0 |
| `\|a` | 归约或 | 只要有一位是 1 就为 1 |
| `~\|a` | 归约或非 | 只要有一位是 1 就为 0 |
| `^a` | 归约异或 | 1 的个数为奇数则为 1 |
| `~^a` 或 `^~a` | 归约同或 | 1 的个数为偶数则为 1 |

```verilog
wire [3:0] a = 4'b1010;

wire r_and = &a;   // 0
wire r_or  = |a;   // 1
wire r_xor = ^a;   // 0，1 的个数为 2，偶数
```

`^a` 常用于奇偶校验。

## 6. ⭐【重点·重复】移位运算符（详见第 6 章）

| 运算符 | 名称 | 说明 |
|---|---|---|
| `<<` | 逻辑左移 | 低位补 0 |
| `>>` | 逻辑右移 | 高位补 0 |
| `<<<` | 算术左移 | 同 `<<` |
| `>>>` | 算术右移 | 高位补符号位 |

```verilog
wire [3:0] a = 4'b1010;

wire [3:0] l = a << 1;    // 4'b0100
wire [3:0] r = a >> 1;    // 4'b0101
wire signed [3:0] s = 4'b1010;
wire signed [3:0] ar = s >>> 1;  // 4'b1101
```

## 7. ⭐【重点·重复】拼接与复制（详见第 6 章）

| 运算符 | 名称 | 例子 |
|---|---|---|
| `{ }` | 拼接 | `{a, b}` |
| `{N{ }}` | 复制 | `{2{a}}` |

```verilog
wire [3:0] a = 4'b1010;
wire [1:0] b = 2'b11;
wire [5:0] c = {a, b};     // 6'b101011
wire [7:0] d = {2{a}};     // 8'b10101010
```

## 8. 条件运算符

| 运算符 | 名称 | 说明 |
|---|---|---|
| `?:` | 三目 | `sel ? a : b` |

```verilog
assign y = sel ? b : a;   // 2 选 1 MUX
```

可嵌套：

```verilog
assign y = sel0 ? a :
           sel1 ? b :
           sel2 ? c : d;
```

对应优先级 MUX 链。

## 9. 赋值运算符

| 运算符 | 名称 | 说明 |
|---|---|---|
| `=` | 阻塞赋值 | 组合逻辑，顺序执行 |
| `<=` | 非阻塞赋值 | 时序逻辑，同时更新 |
| `+=` | 累加 | `a += b` 等价 `a = a + b` |
| `-=` | 累减 | `a -= b` |
| `*=` | 累乘 | `a *= b` |
| `/=` | 累除 | `a /= b` |
| `&=` | 按位与赋值 | `a &= b` |
| `\|=` | 按位或赋值 | `a \|= b` |
| `^=` | 按位异或赋值 | `a ^= b` |
| `<<=` | 左移赋值 | `a <<= b` |
| `>>=` | 右移赋值 | `a >>= b` |

> 【不常用】复合赋值（`+=`、`&=`、`<<=` 等）在 Verilog 里较少用，可综合，但可读性一般。日常 RTL 基本不写。

## 第二部分：位选、一元运算符与逻辑运算符

## 10. 位选与成员

| 语法 | 说明 |
|---|---|
| `a[3]` | 第 3 位 |
| `a[3:0]` | 第 3 到第 0 位 |
| `a[7-:4]` | 从第 7 位向下 4 位，即 `a[7:4]` |
| `mem[0]` | 数组第 0 个元素 |
| `mem[0][3]` | 第 0 个元素的第 3 位 |

## 11. 一元运算符

| 运算符 | 名称 |
|---|---|
| `+` | 一元正 |
| `-` | 一元负 |
| `!` | 逻辑非 |
| `~` | 按位取反 |
| `&` | 归约与 |
| `~&` | 归约与非 |
| `\|` | 归约或 |
| `~\|` | 归约或非 |
| `^` | 归约异或 |
| `~^` `^~` | 归约同或 |

注意：`&`、`|`、`^` 作为一元时是归约，作为二元时是按位。

```verilog
wire [3:0] a = 4'b1010;

wire y1 = &a;      // 归约与
wire y2 = a & b;   // 按位与
```

## 12. 逻辑运算符

| 运算符 | 名称 | 说明 |
|---|---|---|
| `&&` | 逻辑与 | 两边都非零则为 1 |
| `\|\|` | 逻辑或 | 任一边非零则为 1 |
| `!` | 逻辑非 | 操作数为零则为 1 |

结果都是 1 位。

```verilog
wire a = 4'b1010;
wire b = 4'b0000;

wire y1 = a && b;   // 1'b0，因为 b 为零
wire y2 = a || b;   // 1'b1，因为 a 非零
wire y3 = !a;       // 1'b0，因为 a 非零
wire y4 = !b;       // 1'b1，因为 b 为零
```

记忆：

> **一个 `&` 是按位，两个 `&&` 是逻辑。**
> **一个 `|` 是按位，两个 `||` 是逻辑。**
> **一个 `~` 是按位取反，一个 `!` 是逻辑非。**

## 13. 相等运算符

| 运算符 | 名称 | 说明 |
|---|---|---|
| `==` | 逻辑相等 | 结果 1 位，含 x/z 时结果为 x |
| `!=` | 逻辑不等 | 同上 |
| `===` | 全等 | 含 x/z 也精确比较，结果 0/1 |
| `!==` | 不全等 | 同上 |

区别：

```verilog
4'b1010 == 4'b1010    // 1
4'b1010 == 4'b10x0    // x，因为有一位是 x
4'b1010 === 4'b10x0   // 0，精确比较，不相等
4'b10x0 === 4'b10x0   // 1，精确比较，相等
```

> 【不常用】`===`、`!==` 主要用于仿真/testbench，一般不综合。

## 第三部分：优先级、位宽与陷阱

## 14. 完整优先级表

从**高到低**：

| 优先级 | 运算符 | 说明 |
|---|---|---|
| 1 | `()` | 括号 |
| 2 | `! ~ + -` | 一元非、按位取反、一元正负 |
| 3 | `**` | 幂 |
| 4 | `* / %` | 乘除模 |
| 5 | `+ -` | 二元加减 |
| 6 | `<< >> <<< >>>` | 移位 |
| 7 | `< <= > >=` | 关系 |
| 8 | `== != === !==` | 相等 |
| 9 | `&` | 按位与 |
| 10 | `^ ~^ ^~` | 按位异或、同或 |
| 11 | `\|` | 按位或 |
| 12 | `&&` | 逻辑与 |
| 13 | `\|\|` | 逻辑或 |
| 14 | `?:` | 条件 |
| 15 | `{ }` | 拼接 |
| 16 | `=` `<=` | 赋值 |

注意：

- 归约运算符和一元运算符同级；
- 拼接优先级很低，低于条件运算符；
- 赋值优先级最低。

## 15. 优先级陷阱

**15.1 按位与 vs 相等**

```verilog
wire y = a & b == c;
```

实际是：

```verilog
wire y = a & (b == c);
```

因为 `==` 优先级高于 `&`。
如果本意是 `(a & b) == c`，必须加括号：

```verilog
wire y = (a & b) == c;
```

**15.2 移位 vs 加减**

```verilog
wire y = a + b << 1;
```

实际是：

```verilog
wire y = (a + b) << 1;
```

因为 `+` 优先级高于 `<<`。
如果本意是 `a + (b << 1)`，要加括号。

**15.3 逻辑与 vs 按位与**

```verilog
wire y = a & b && c;
```

实际是：

```verilog
wire y = (a & b) && c;
```

因为 `&` 优先级高于 `&&`。
可读性差，建议加括号。

**15.4 条件运算符**

```verilog
wire y = a ? b : c + d;
```

实际是：

```verilog
wire y = a ? b : (c + d);
```

因为 `+` 优先级高于 `?:`。

**15.5 拼接**

```verilog
wire y = {a, b} + c;
```

实际是：

```verilog
wire y = ({a, b}) + c;
```

拼接先算，再加。

## 16. ⭐【重点·重复】位宽与运算符

运算符的结果位宽规则：

- 算术、按位运算：结果位宽取两个操作数中较大的；
- 关系、逻辑、归约：结果 1 位；
- 移位：结果位宽等于左边操作数的位宽；
- 拼接：结果位宽等于各部分之和；
- 条件：结果位宽取两个分支中较大的。

例子：

```verilog
wire [3:0] a = 4'b1010;
wire [7:0] b = 8'hFF;
wire [7:0] y = a & b;   // a 先扩展成 8 位
```

```verilog
wire [3:0] a = 4'b1010;
wire [3:0] y = a << 1;   // 结果还是 4 位，高位丢
wire [4:0] z = a << 1;   // 结果 5 位，高位保留
```

建议：

- 显式写位宽，避免隐式扩展；
- 需要保留高位时先扩展再移位；
- 混合有符号/无符号时特别小心。

## 17. 有符号与无符号运算

规则：

- 只要有一个操作数是无符号，整个表达式按无符号处理；
- 有符号数会先扩展成无符号，符号位可能丢失；
- 混合运算容易出错，建议显式 `$signed` / `$unsigned`。

```verilog
wire signed [7:0] a = 8'shFF;   // -1
wire        [7:0] b = 8'h01;    // 1

wire signed [8:0] c = a + b;    // 容易出错
```

`a` 被当成无符号 255，结果是 256，不是 0。
正确写法：

```verilog
wire signed [8:0] c = $signed(a) + $signed(b);
```

## 18. 常见运算符使用建议

| 场景 | 推荐写法 |
|---|---|
| 组合逻辑 | `assign y = ...;` |
| 多路选择 | `assign y = sel ? a : b;` |
| 复杂组合 | `always @(*)` + `if/case` |
| 时序逻辑 | `always @(posedge clk)` + `<=` |
| 移位 | `<<`、`>>`，或拼接 |
| 循环移位 | 拼接 |
| 符号扩展 | `{{N{a[MSB]}}, a}` |
| 零扩展 | `{{N{1'b0}}, a}` |
| 奇偶校验 | `^a` |
| 掩码 | `a & mask` |
| 置位 | `a \| mask` |
| 清位 | `a & ~mask` |
| 翻转 | `a ^ mask` |
| 比较 | 加括号明确 |
| 混合有符号 | `$signed` / `$unsigned` |

## 19. 完整例子

```verilog
module op_demo(
    input  wire [7:0] a,
    input  wire [7:0] b,
    input  wire       sel,
    output wire [7:0] y_arith,
    output wire [7:0] y_bit,
    output wire       y_rel,
    output wire       y_logic,
    output wire       y_reduce,
    output wire [7:0] y_shift,
    output wire [15:0] y_cat,
    output wire [7:0] y_mux
);

    // 算术
    assign y_arith = a + b;

    // 按位
    assign y_bit = a & b;

    // 关系
    assign y_rel = (a > b);

    // 逻辑
    assign y_logic = (a != 0) && (b != 0);

    // 归约
    assign y_reduce = ^a;

    // 移位
    assign y_shift = a << 1;

    // 拼接
    assign y_cat = {a, b};

    // 条件
    assign y_mux = sel ? a : b;

endmodule
```

## 20. 总结口诀

> **算术：`+ - * / %`，除法取整，模跟被除数。**
> **关系：`< <= > >=`，结果 1 位。**
> **相等：`== !=` 含 x/z 出 x，`=== !==` 精确比较。**
> **逻辑：`&& || !`，结果 1 位。**
> **按位：`~ & | ^ ~^`，对应位算。**
> **归约：`& ~& | ~| ^ ~^`，多位压 1 位。**
> **移位：`<< >> <<< >>>`，位宽看左边。**
> **拼接：`{ } {N{ }}`，左高位右低位。**
> **条件：`?:`，相当于 MUX。**
> **优先级：括号最高，赋值最低，不确定就加括号。**
> **位宽：较大者决定结果，移位看左边，拼接相加。**
> **有符号混合无符号，容易出错，显式转换。**

读代码时遇到复杂表达式，先按优先级加括号还原，再确认位宽，最后判断综合出什么硬件。这样就不会被运算符优先级和位宽陷阱坑到。

---

# 11. 数据类型与数字表示

> 本章把新目录的"**11. 数据类型与数字表示**"合为一章：第 1 节是原笔记的"数据类型"章，第 2 节是原笔记的"数字的表示格式"章。两节的小节编号保持原样，只做层级下调，内容未删。
> ⭐【重点·重复】"**常量要指定位宽**"（如 `1'b1`、`8'hFF`）在第 6 章（拼接）、第 10 章（运算符）都出现过，这里再讲一次——**重复出现说明它是重点**，这是初学最常踩的坑。

## 1. 数据类型（原笔记"数据类型"章）

Verilog 的数据类型，核心就分两大类：

> **net 类型**：表示"连线"，如 `wire`，必须被驱动，不存储。
> **variable 类型**：表示"变量"，如 `reg`，在过程块里被赋值，仿真中能保持值。

但 Verilog 还有常量、参数、整数、数组、有符号数等。下面按类别讲清楚。

### 1.1 四值逻辑

Verilog 里每个 bit 有 4 种状态：

| 值 | 含义 |
|---|---|
| `0` | 逻辑 0 |
| `1` | 逻辑 1 |
| `x` | 未知，仿真初值、冲突等 |
| `z` | 高阻，未驱动、三态总线释放 |

所以：

```verilog
wire a;        // 未驱动时是 z
reg  b;        // 未赋值时是 x
```

注意：`x` 和 `z` 是仿真概念，实际硬件里最终会变成 0 或 1，但仿真时很重要。

### 1.2 net 类型：wire 及其家族

net 表示连线，必须由驱动源驱动。

| 类型 | 含义 |
|---|---|
| `wire` | 普通连线，最常用 |
| `tri` | 三态线，和 wire 类似 |
| `wand` | 线与：多驱动时按与解析 |
| `wor` | 线或：多驱动时按或解析 |
| `tri0` | 无驱动时为 0 |
| `tri1` | 无驱动时为 1 |
| `supply0` | 常量 0 |
| `supply1` | 常量 1 |

日常 RTL 里 **99% 只用 `wire`**。

```verilog
wire y;
wire [7:0] data;
wire [3:0] bus;
```

驱动方式：

```verilog
assign y = a & b;

sub u_sub(
    .out(y)
);
```

特点：

- 不能存储；
- 必须被驱动；
- 可多驱动，靠 net 解析；
- `inout` 必须用 wire。

> 【不常用】`tri`、`wand`、`wor`、`tri0`、`tri1`、`supply0`、`supply1` 这些 net 家族成员在普通 FPGA RTL 里基本不用，知道有它们即可。

### 1.3 variable 类型：reg 及其家族

variable 表示过程赋值变量，在 `always` / `initial` 里赋值。

| 类型 | 含义 | 可综合 |
|---|---|---|
| `reg` | 过程变量，最常用 | 是 |
| `integer` | 32 位有符号整数 | 常用于循环、仿真 |
| `time` | 64 位无符号时间 | 仿真 |
| `real` | 浮点数 | 一般不可综合 |
| `realtime` | 浮点时间 | 仿真 |
| `event` | 事件 | 仿真 |

**reg**

```verilog
reg q;
reg [7:0] data;
always @(posedge clk)
    q <= d;
```

再次强调：

> **reg 不等于寄存器。**
> 在 `always @(*)` 里，它综合成组合逻辑；
> 在 `always @(posedge clk)` 里，它才综合成触发器。

**integer**

```verilog
integer i;
always @(*) begin
    for (i = 0; i < 4; i = i + 1)
        y[i] = a[i] & b[i];
end
```

`integer` 是 32 位有符号，常用于循环变量。
可综合，但不要用它存硬件数据，只用于循环索引。

**real / time / event**

一般只用于 testbench 或仿真，不可综合。

```verilog
real r;
time t;
event ev;
```

> 【不常用】`real`、`realtime`、`time`、`event` 只在 testbench/仿真里用，RTL 设计里不出现。

### 1.4 wire 和 reg 的选择

⭐【重点·重复】这张表在第 4 章"wire / reg / logic"里已完整讲过（并附判断口诀），此处保留作为数据类型章的对照。

| 场景 | 用 |
|---|---|
| `assign` 左边 | `wire` |
| `always` 左边 | `reg` |
| 模块输出接子模块输出 | `wire` |
| `inout` 双向 | `wire` |
| 多驱动 | `wire` |
| 时序逻辑存储 | `reg` |
| 组合逻辑过程赋值 | `reg` |

SystemVerilog 里单驱动可以统一用 `logic`，但多驱动、双向仍用 `wire`。

### 1.5 向量与位宽

```verilog
wire [7:0] a;        // 8 位 wire，a[7] 是 MSB，a[0] 是 LSB
reg  [3:0] b;        // 4 位 reg
wire [31:0] data;    // 32 位
```

位选：

```verilog
a[0]       // 第 0 位
a[3:1]     // 第 3 到第 1 位
a[7]       // MSB
```

位宽决定能表示的状态数：

```text
N 位 -> 2^N 种状态
无符号范围：0 ~ 2^N - 1
有符号范围：-2^(N-1) ~ 2^(N-1)-1
```

### 1.6 有符号与无符号

默认都是无符号。

```verilog
wire [7:0] a;              // 无符号
wire signed [7:0] b;       // 有符号
reg signed [15:0] c;       // 有符号
```

有符号数最高位是符号位：

```verilog
8'b11111111   // 无符号：255
8'sb11111111  // 有符号：-1
```

常量表示：

```verilog
8'b1010_1010     // 二进制，无符号
8'hFF            // 十六进制
8'd255           // 十进制
8'sd255          // 有符号十进制
4'b10xz          // 包含 x/z
```

建议：

- 常量最好指定位宽和进制；
- 有符号运算要小心扩展和截断；
- 混合有符号/无符号时，Verilog 会按无符号处理，容易出错。

### 1.7 常量与参数

**常量**

```verilog
8'hFF
4'b1010
16'd1000
1'b0
1'b1
```

**parameter**

模块级常量，可在实例化时覆盖：

```verilog
module sub #(
    parameter WIDTH = 8
)(
    input  wire [WIDTH-1:0] data
);
endmodule
```

实例化：

```verilog
sub #(.WIDTH(16)) u_sub(
    .data(data16)
);
```

**localparam**

模块内部常量，不能被外部覆盖：

```verilog
localparam IDLE = 2'b00;
localparam RUN  = 2'b01;
```

常用于状态机编码。

（参数化模块的完整用法见第 12 章）

### 1.8 数组与存储器

Verilog 里可以定义数组：

```verilog
reg [7:0] mem [0:255];   // 256 个 8 位寄存器，即一个存储器
wire [7:0] rom [0:15];   // 16 个 8 位 wire
```

访问：

```verilog
mem[0]      // 第 0 个 8 位数据
mem[0][3]   // 第 0 个数据的第 3 位
```

注意：

- 左边是位宽，右边是深度；
- `mem` 本身不是一个 256*8 的宽信号，而是一组 8 位变量；
- 可综合成 RAM/ROM，取决于写法。

多维数组：

```verilog
reg [7:0] matrix [0:3][0:3];
```

SystemVerilog 支持更多数组类型。

### 1.9 SystemVerilog 新增类型

SystemVerilog 扩展了很多类型，常用：

| 类型 | 含义 |
|---|---|
| `logic` | 四值逻辑，可替代 wire/reg 单驱动场景 |
| `bit` | 二值逻辑，只有 0/1 |
| `byte` | 8 位有符号 |
| `shortint` | 16 位有符号 |
| `int` | 32 位有符号 |
| `longint` | 64 位有符号 |
| `enum` | 枚举，常用于状态机 |
| `struct` | 结构体 |
| `union` | 联合体 |

例子：

```verilog
logic [7:0] data;
logic       valid;

typedef enum logic [1:0] {
    IDLE,
    RUN,
    DONE
} state_t;

state_t state;
```

注意：

- `logic` 单驱动很方便，但多驱动、`inout` 仍必须 `wire`；
- `bit` 是二值，仿真更快，但不表示 x/z；
- `enum` 让状态机更可读。

> 【不常用】`struct`、`union`、`longint` 等在普通 FPGA 竞赛/工程 RTL 里很少用；`logic`、`enum`、`typedef` 在 SystemVerilog 工程里较常见。

### 1.10 可综合 vs 不可综合

| 类型 | 可综合 | 说明 |
|---|---|---|
| `wire` | 是 | 连线 |
| `reg` | 是 | 过程变量，看 always 类型 |
| `logic` | 是 | SV 常用 |
| `integer` | 是 | 常用于循环，不建议存数据 |
| `parameter` / `localparam` | 是 | 常量 |
| `real` | 否 | 仿真 |
| `time` | 否 | 仿真 |
| `event` | 否 | 仿真 |
| `string` | 否 | 仿真 |

实际 RTL 设计里，常用就这些：

```verilog
wire
reg
parameter
localparam
integer（循环）
```

SystemVerilog 再加：

```verilog
logic
enum
typedef
```

（可综合性的汇总见第 19 章）

### 1.11 完整例子

```verilog
module data_type_demo #(
    parameter WIDTH = 8
)(
    input  wire                clk,
    input  wire                rst_n,
    input  wire [WIDTH-1:0]    a,
    input  wire [WIDTH-1:0]    b,
    input  wire                sel,
    output wire [WIDTH-1:0]    y_comb,
    output reg  [WIDTH-1:0]    y_seq
);

    // wire：组合逻辑连线
    wire [WIDTH-1:0] and_out;
    assign and_out = a & b;

    // reg：组合逻辑过程赋值
    reg [WIDTH-1:0] mux_out;
    always @(*) begin
        if (sel)
            mux_out = a;
        else
            mux_out = b;
    end

    assign y_comb = mux_out & and_out;

    // reg：时序逻辑，综合成触发器
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            y_seq <= {WIDTH{1'b0}};
        else
            y_seq <= a + b;
    end

    // localparam：状态编码
    localparam IDLE = 2'b00;
    localparam RUN  = 2'b01;

    // integer：循环变量
    integer i;
    always @(*) begin
        for (i = 0; i < WIDTH; i = i + 1)
            ; // 示例
    end

endmodule
```

### 1.12 数据类型总结口诀

> **net 是线：wire，必须驱动，不存储。**
> **variable 是变量：reg，过程赋值，看 always 定硬件。**
> **四值逻辑：0、1、x、z。**
> **常量指定位宽：8'hFF、4'b1010。**
> **parameter 可覆盖，localparam 内部常量。**
> **integer 用于循环，real/time 只仿真。**
> **数组：`reg [7:0] mem [0:255]`。**
> **SystemVerilog 用 logic，多驱动还得 wire。**

读代码时先看类型，再看它在哪赋值，就能判断它对应连线、组合逻辑还是触发器。

---

## 2. 数字的表示格式（原笔记"数字的表示格式"章）

Verilog 里数字的表示格式，核心就一句话：

> **`<位宽>'<进制><数值>`**
> 例如：`8'hFF`、`4'b1010`、`16'd1000`。

下面按部分讲清楚。

### 2.1 基本格式

```text
<位宽>'<进制><数值>
```

例子：

```verilog
8'hFF        // 8 位十六进制 FF
4'b1010      // 4 位二进制 1010
16'd1000     // 16 位十进制 1000
8'o77        // 8 位八进制 77
```

其中：

- **位宽**：可省略，省略时默认至少 32 位；
- **单引号 `'`**：分隔位宽和进制；
- **进制符号**：`b`、`o`、`d`、`h`；
- **数值**：对应进制的数字，可带下划线。

进制符号大小写不敏感：

```verilog
8'hFF
8'HFF
8'hff   // 都一样
```

### 2.2 四种进制

| 符号 | 进制 | 例子 | 说明 |
|---|---|---|---|
| `b` 或 `B` | 二进制 | `4'b1010` | 0、1、x、z |
| `o` 或 `O` | 八进制 | `6'o52` | 0~7 |
| `d` 或 `D` | 十进制 | `8'd255` | 0~9 |
| `h` 或 `H` | 十六进制 | `8'hFF` | 0~9、A~F |

如果省略进制符号，默认是十进制：

```verilog
8'FF      // 错？实际上 8'FF 不合法，必须写 8'hFF
8'd255    // 正确
```

但有一种写法：

```verilog
' d 255   // 合法，省略位宽，默认 32 位
```

### 2.3 位宽

[位宽](位宽本质.md)决定了这个常量有多少 bit。

```verilog
4'b1010     // 4 位
8'hFF       // 8 位
16'd1000    // 16 位
32'hDEADBEEF // 32 位
```

**省略位宽**

```verilog
'd255       // 默认至少 32 位
'hFF        // 默认至少 32 位
255         // 十进制，默认 32 位有符号
```

建议：**总是显式写位宽**，避免隐式扩展或截断。

**位宽不足或超出**

如果数值需要的位数超过指定位宽，高位被截断：

```verilog
4'd16       // 16 需要 5 位，截断为 4'b0000，即 0
4'hFF       // 8 位 FF 截断为 4 位，即 4'hF
```

如果目标位宽更宽，会扩展：

```verilog
8'd10       // 8'b00001010
8'hFF       // 8'b11111111
```

### 2.4 有符号与无符号

默认是无符号。加 `s` 表示有符号：

```verilog
8'd255      // 无符号，255
8'sd255     // 有符号，8 位放不下 255，按补码解释为 -1
8'shFF      // 有符号，-1
8'sd-1      // 有符号，-1
```

常见写法：

```verilog
8'shFF      // -1
8'sd127     // 127
8'sd-128    // -128
```

注意：

- 有符号数最高位是符号位；
- 混合有符号和无符号时，Verilog 通常按无符号处理，容易出错；
- 负数建议直接用有符号常量或补码。

### 2.5 x 和 z

Verilog 有四种逻辑值：`0`、`1`、`x`、`z`。

```verilog
4'b10xz     // 4 位：1、0、x、z
4'bx        // 4 位全 x
4'bz        // 4 位全 z
8'hx        // 8 位全 x
8'hz        // 8 位全 z
```

`?` 在数字里通常等价于 `z`，但在 `case` 里表示不关心：

```verilog
4'b1?0?     // 等价于 4'b1z0z
```

`x` 表示未知，`z` 表示高阻。仿真里很重要，实际硬件最终会变成 0 或 1。

### 2.6 下划线

下划线只用于提高可读性，会被忽略：

```verilog
32'hDEAD_BEEF
16'b1010_1010_1010_1010
8'd1_000     // 十进制 1000
```

### 2.7 特殊常量（SystemVerilog）

SystemVerilog 支持简写：

```verilog
'0          // 所有位为 0
'1          // 所有位为 1
'x          // 所有位为 x
'z          // 所有位为 z
```

例如：

```verilog
logic [7:0] a = '0;    // 8'b00000000
logic [7:0] b = '1;    // 8'b11111111
```

这在复位、初始化时很方便。

### 2.8 无位宽常量

```verilog
10          // 十进制，默认 32 位有符号
-5          // 一元负，结果通常 32 位有符号
'hFF        // 十六进制，默认至少 32 位
'b1010      // 二进制，默认至少 32 位
```

建议：在 RTL 里尽量写完整：

```verilog
8'd10
8'hFF
4'b1010
```

### 2.9 实数与时间

实数用于仿真，不可综合：

```verilog
1.5
1e3         // 1000.0
1.2e-3      // 0.0012
```

时间常量用于仿真：

```verilog
10ns
1.5us
#10         // 延迟 10 个时间单位
```

字符串也主要用于仿真：

```verilog
"Hello"
```

> 【不常用】实数、时间常量、字符串只在 testbench/仿真里用，RTL 里不出现。

### 2.10 常见例子汇总

| 写法 | 含义 |
|---|---|
| `4'b1010` | 4 位二进制 1010 |
| `8'hFF` | 8 位十六进制 FF |
| `16'd1000` | 16 位十进制 1000 |
| `8'o77` | 8 位八进制 77 |
| `8'shFF` | 8 位有符号，-1 |
| `4'b10xz` | 4 位，包含 x 和 z |
| `32'hDEAD_BEEF` | 带下划线的 32 位十六进制 |
| `'0` | 所有位为 0（SV） |
| `'1` | 所有位为 1（SV） |
| `1.5` | 实数 |
| `10ns` | 时间常量 |

### 2.11 常见陷阱

**1. 位宽不够被截断**

```verilog
4'd16       // 结果是 0，不是 16
```

**2. ⭐【重点·重复】默认 32 位**

```verilog
assign y = a + 1;   // 1 是 32 位，可能影响位宽
```

最好写：

```verilog
assign y = a + 1'b1;
```

**3. 有符号和无符号混合**

```verilog
wire signed [7:0] a = 8'shFF;  // -1
wire [7:0] b = 8'hFF;          // 255
wire [8:0] c = a + b;          // 容易出错
```

**4. 常量不写进制**

```verilog
8'FF        // 错，必须写 8'hFF
```

**5. 下划线位置**

```verilog
16'h_FF     // 可以，但一般写在数字中间
16'hFF_     // 也可以，但不推荐
```

### 2.12 数字表示总结口诀

> **格式：位宽 ' 进制 数值，如 `8'hFF`。**
> **进制：b 二进制，o 八进制，d 十进制，h 十六进制。**
> **加 s 是有符号，不加是无符号。**
> **x 未知，z 高阻，? 常等价 z。**
> **下划线只为好看，会被忽略。**
> **省略位宽默认 32 位，建议总是写全。**
> **位宽不够会截断，位宽更宽会扩展。**
> **SystemVerilog 可用 `'0`、`'1`、`'x`、`'z`。**

读代码时看到数字，先看位宽，再看进制，再看有没有 `s`，就能知道它的确切值和类型。

---

# 12. 模块例化与参数化

端口映射就是**模块实例化时，把外层信号连接到子模块端口上**。它是 Verilog 里层次化设计的关键：大模块由小模块拼起来，靠的就是端口映射。

一句话：

> **端口映射 = 给子模块的每个端口"接线"。**

## 1. 两种映射方式

假设子模块：

```verilog
module sub(
    input  wire       clk,
    input  wire       rst_n,
    input  wire [7:0] data_in,
    output wire [7:0] data_out
);
    assign data_out = data_in + 1'b1;
endmodule
```

### 1.1 按位置映射（顺序连接）

```verilog
sub u_sub(
    clk,
    rst_n,
    data_in,
    data_out
);
```

规则：

- 顺序必须和子模块端口声明顺序**完全一致**；
- 位宽也要匹配；
- 容易出错，端口一改就全乱。

### 1.2 按名称映射（推荐）

```verilog
sub u_sub(
    .clk      (clk),
    .rst_n    (rst_n),
    .data_in  (data_in),
    .data_out (data_out)
);
```

规则：

- `.端口名(外层信号)`；
- 顺序无所谓；
- 可读性强，端口增减不影响其他连接；
- 工程里**推荐一律用按名称映射**。

## 2. 语法格式

```verilog
模块名 实例名(
    .端口名1(信号1),
    .端口名2(信号2),
    ...
);
```

- `模块名`：子模块的名字；
- `实例名`：这次实例化的唯一名字，同一模块可以实例化多次，实例名不能重复；
- `.端口名`：子模块声明里的端口名；
- `(信号)`：当前模块里的信号或表达式。

例子：

```verilog
sub u_sub0(
    .clk      (clk),
    .rst_n    (rst_n),
    .data_in  (a),
    .data_out (y0)
);

sub u_sub1(
    .clk      (clk),
    .rst_n    (rst_n),
    .data_in  (b),
    .data_out (y1)
);
```

同一个 `sub` 实例化两次，用不同实例名和不同信号。

## 3. 端口方向与连接信号类型

⭐【重点·重复】"输入由外层驱动、输出接 wire、inout 必须 wire"在第 3 章、第 4 章都出现过，此处第三次出现，是端口相关最核心的规则。

| 子模块端口方向 | 外层连接信号 | 说明 |
|---|---|---|
| `input` | wire / reg / 表达式 | 外层驱动子模块 |
| `output` | wire | 子模块驱动外层 |
| `inout` | wire | 双向，必须 wire |

关键：

- 子模块 `input` 由外层驱动，所以外层信号必须有驱动源；
- 子模块 `output` 驱动外层，所以外层必须用 `wire` 接收；
- `inout` 必须用 `wire`。

例子：

```verilog
module top(
    input  wire       clk,
    input  wire       rst_n,
    input  wire [7:0] a,
    output wire [7:0] y
);

    wire [7:0] sub_out;

    sub u_sub(
        .clk      (clk),
        .rst_n    (rst_n),
        .data_in  (a),
        .data_out (sub_out)   // 子模块输出 -> wire
    );

    assign y = sub_out;

endmodule
```

## 4. 位宽不匹配

如果端口位宽和连接信号位宽不一致：

```verilog
sub u_sub(
    .data_in (4'b1010)   // 端口是 8 位，这里只给 4 位
);
```

Verilog 会自动扩展或截断：

- 无符号：高位补 0；
- 有符号：符号扩展；
- 连接信号更宽：截断高位。

建议：

- 位宽尽量一致；
- 常量指定位宽，如 `8'h0A`；
- 避免依赖隐式扩展。

## 5. 端口可以不连

### 5.1 输出端口不连

```verilog
sub u_sub(
    .clk      (clk),
    .rst_n    (rst_n),
    .data_in  (a),
    .data_out ()          // 不关心这个输出
);
```

### 5.2 输入端口不连

```verilog
sub u_sub(
    .clk      (clk),
    .rst_n    (rst_n),
    .data_in  (),         // 悬空，输入为 z
    .data_out (y)
);
```

输入悬空通常不好，可能引入 `x` 或 `z`，仿真时出问题。
如果确实不用，最好显式接一个确定值：

```verilog
.data_in (8'b0)
```

### 5.3 按位置映射时跳过端口

```verilog
sub u_sub(
    clk,
    rst_n,
    ,          // 空着，不推荐
    data_out
);
```

非常不推荐，容易出错。

## 6. 端口连接表达式

端口连接处可以写表达式，不只是简单信号：

```verilog
sub u_sub(
    .clk      (clk),
    .rst_n    (rst_n),
    .data_in  (a + 1'b1),        // 表达式
    .data_out (y)
);
```

也可以拼接：

```verilog
sub u_sub(
    .data_in ({a, b}),
    .data_out (y)
);
```

但注意：

- 表达式会生成组合逻辑；
- 输出端口不能接表达式，只能接 wire。

## 7. 参数化模块的端口映射

如果子模块有参数：

```verilog
module sub #(
    parameter WIDTH = 8
)(
    input  wire             clk,
    input  wire [WIDTH-1:0] data_in,
    output wire [WIDTH-1:0] data_out
);
    assign data_out = data_in;
endmodule
```

实例化时可以用 `#()` 传参数：

```verilog
sub #(
    .WIDTH(16)
) u_sub(
    .clk      (clk),
    .data_in  (a16),
    .data_out (y16)
);
```

也可以按位置传参：

```verilog
sub #(16) u_sub(
    .clk      (clk),
    .data_in  (a16),
    .data_out (y16)
);
```

推荐按名称传参，清晰。

> 【不常用】`defparam` 可以在实例化之外用层次名改参数（`defparam u_sub.WIDTH = 16;`），可读性差且部分工具不推荐，新代码基本不用，优先用 `#()`。

## 8. 常见错误

### 8.1 端口名拼错

```verilog
sub u_sub(
    .clk      (clk),
    .rst_n    (rst_n),
    .data_in  (a),
    .data_out (y),
    .data_o   (z)      // 错！子模块没有 data_o
);
```

### 8.2 输出端口接了 reg

```verilog
reg [7:0] sub_out;

sub u_sub(
    .data_out (sub_out)   // 错！输出端口驱动的是 wire，不是 reg
);
```

### 8.3 位宽搞反

```verilog
sub u_sub(
    .data_in  (y),        // 输入端口连到了输出信号
    .data_out (a)         // 输出端口连到了输入信号
);
```

方向反了，编译可能过，但功能错。

### 8.4 实例名重复

```verilog
sub u_sub(...);
sub u_sub(...);   // 错！实例名重复
```

同一模块多次实例化，实例名必须不同。

### 8.5 按位置映射顺序错

```verilog
sub u_sub(
    rst_n,     // 错！第一个端口是 clk
    clk,
    data_in,
    data_out
);
```

顺序错了，编译可能过，但功能完全错。

## 9. 完整例子

```verilog
// 子模块：8 位加法器
module adder8(
    input  wire [7:0] a,
    input  wire [7:0] b,
    input  wire       cin,
    output wire [7:0] sum,
    output wire       cout
);
    assign {cout, sum} = a + b + cin;
endmodule

// 顶层：实例化两个加法器
module top(
    input  wire [7:0] x,
    input  wire [7:0] y,
    input  wire [7:0] z,
    output wire [7:0] sum1,
    output wire [7:0] sum2
);

    wire cout1;

    // 第一个加法器：x + y
    adder8 u_add1(
        .a    (x),
        .b    (y),
        .cin  (1'b0),
        .sum  (sum1),
        .cout (cout1)
    );

    // 第二个加法器：sum1 + z
    adder8 u_add2(
        .a    (sum1),
        .b    (z),
        .cin  (cout1),
        .sum  (sum2),
        .cout ()          // 不关心
    );

endmodule
```

对应硬件：

```text
x ──┐
    ├── adder8 ──> sum1 ──┐
y ──┘                     ├── adder8 ──> sum2
z ────────────────────────┘
```

## 10. 模块实例化补充（来自三天速成笔记）

【补全·来源：`02三天入门verilog速成.md`】

### 10.1 设计思路

设计复杂电路时，可先做底层模块（如 D 触发器），再在顶层模块中调用。

**底层模块：D 触发器**

```verilog
module DFF(clock, D, Q);
    input clock, D;
    output Q;
    reg Q;

    always @ (posedge clock)
        Q = D;
endmodule
```

**顶层模块：调用两个 DFF**

```verilog
module exam(clock, D, Q);
    input clock, D;
    output Q;
    wire D1, Q1;      // 内部连线变量

    // 实例化第一个 DFF
    DFF DFF1(
        .clock(clock),
        .D(D),
        .Q(Q1)
    );

    // 实例化第二个 DFF
    DFF DFF2(
        .clock(clock),
        .D(D1),         // 此处应接到第一级输出，示例略
        .Q(Q)
    );
endmodule
```

### 10.2 实例化格式

```verilog
模块名 实例化名(端口映射);
```

- **实例化名不能省略**
- 实例化名可任意（如 `DFF1`、`DFF2`、`abc` 都可），但应避免与端口名冲突
- 顶层模块中需声明内部连线变量（如 `D1`、`Q1`）

### 10.3 端口映射的两种方法

**① 端口名关联法（推荐）**

```verilog
.底层端口名(外部信号)
```

格式清晰，**不必按底层模块端口顺序写**。

```verilog
DFF DFF1(
    .clock(clock),
    .D(D),
    .Q(Q1)
);
```

> 最后一个端口映射后**不加逗号**。

**② 位置关联法（不推荐）**

按底层模块端口列表的顺序逐个传入，代码可读性差，应避免使用。

## 11. 总结口诀

> **端口映射就是接线：`.端口名(信号)`。**
> **推荐按名称，不推荐按位置。**
> **输入由外层驱动，输出接 wire，inout 必须 wire。**
> **输出端口不能接 reg，不能接表达式。**
> **位宽要匹配，常量指定位宽。**
> **实例名不能重复，端口名不能拼错。**
> **参数化模块用 `#()` 传参。**

读代码时看到模块实例化，先找 `.端口名(信号)`，再确认每个信号的方向和位宽，就能还原出模块之间的连接关系。

---

# 13. generate / function / task

> ⚠️ **本章是补全章节**：原笔记只有"模块例化"和零散的"for 循环展开"内容，没有系统的 generate / function / task 章节。
> 本章内容标注 `【补全】`，来源为 Verilog-2001 通用语法 + 知识库中 [always语句.md](always语句.md)、[02三天入门verilog速成.md](../三天入门Verilog俗称/02三天入门verilog速成.md) 的相关片段。
> 【不常用】`function` / `task` 在竞赛与入门 RTL 里使用频率不高（`function` 偶尔用于组合计算，`task` 多用于 testbench），阅读时知道有这两个东西即可。

## 1. [generate：用代码"批量造硬件"](generate生成语句.md)

generate 语句用来在**编译/综合时**根据常量条件或循环，生成多份重复的硬件结构。它和 always 里的 `for` 是"表亲"，但 generate 生成的是**模块级**语句（例化、assign、always 块都可以）。

> ⭐【重点·重复】"`for` 不是运行时循环，而是展开成多份硬件"这条在第 1 章、第 7 章都出现过，generate 是同一思想的模块级版本。

### 1.1 generate for：批量例化 / 批量连线

```verilog
genvar i;
generate
    for (i = 0; i < 8; i = i + 1) begin : gen_bit
        assign y[i] = a[i] & b[i];
    end
endgenerate
```

等价于手写 8 条 `assign`。

批量例化子模块：

```verilog
genvar i;
generate
    for (i = 0; i < 4; i = i + 1) begin : gen_stage
        dff u_dff (
            .clk (clk),
            .d   (d[i]),
            .q   (q[i])
        );
    end
endgenerate
```

要点：

- 循环变量用 `genvar` 声明；
- 循环次数必须是**常量**（`parameter` 或字面量），不能是运行时变量；
- `begin : 名字` 给每份生成块起层次名（推荐，便于仿真时定位信号，如 `gen_stage[0].u_dff.q`）。

### 1.2 generate if / case：条件生成

```verilog
generate
    if (WIDTH == 8) begin : gen_8
        assign y = a;
    end else begin : gen_wide
        assign y = a[7:0];
    end
endgenerate
```

`case` 版本：

```verilog
generate
    case (MODE)
        0: assign y = a;
        1: assign y = b;
        default: assign y = 1'b0;
    endcase
endgenerate
```

要点：条件必须是**常量表达式**（参数/`localparam`），在综合前就能确定，所以生成结果在硬件上是固定的，不会综合出 MUX。

### 1.3 generate 与 always 里 for 的区别

| 对比 | `generate for` | `always` 里的 `for` |
|---|---|---|
| 位置 | 模块级（和 assign、例化同级） | 过程块内部 |
| 能生成什么 | 例化、assign、always 块 | 只能生成过程赋值语句 |
| 典型用途 | 批量例化子模块、批量连线 | 批量赋值 `y[i] = a[i] & b[i]` |
| 循环变量 | `genvar` | `integer` |

## 2. function：组合逻辑函数

`function` 用来把一段**纯组合**计算封装成函数，在 `assign` 或 `always` 里调用，避免重复写同样的表达式。

基本格式：

```verilog
function [7:0] add8;
    input [7:0] a;
    input [7:0] b;
    begin
        add8 = a + b;
    end
endfunction
```

调用：

```verilog
assign y = add8(x, z);
```

要点：

- 函数**必须有返回值**，返回值就是函数名本身（上面例子里的 `add8`）；
- 函数**只能写组合逻辑**：不能有时钟、不能有 `#` 延时、不能有 `@`、不能有 `wait`；
- 函数内不能例化模块；
- 参数是按值传递的（只读，不能在函数里改）；
- 综合出来是一块组合逻辑，**不是**把硬件"复用"，调用几次就复制几份。

常见用法：位宽计算、简单算术、编解码。

```verilog
function integer clogb2;
    input integer value;
    integer i;
    begin
        clogb2 = 0;
        for (i = value - 1; i > 0; i = i >> 1)
            clogb2 = clogb2 + 1;
    end
endfunction

localparam DEPTH = 16;
localparam ADDR_W = clogb2(DEPTH);   // 4
```

> 注意：不要用 `function` 写分支不全的逻辑——函数里没赋值到的情况同样会综合出锁存器。

## 3. task：过程任务

`task` 用来封装一段**过程代码**，可以在 `initial` / `always` 里调用，可以有多条语句、可以有延时、可以有多个输出。

基本格式：

```verilog
task disp;
    input [7:0] value;
    begin
        $display("value = %d", value);
        #10;
    end
endtask
```

调用：

```verilog
initial begin
    disp(8'd5);
end
```

要点：

- task **可以有 0 个或多个输出**（用 `output` / `inout` 参数带回结果）；
- task 内**可以有延时 `#`、事件控制 `@`**，所以主要用于**仿真**；
- 可综合的 task（不含延时、只做组合赋值）在 RTL 里能用，但可读性不如直接写；
- 和 `function` 一样，调用不会"复用硬件"，是就地展开。

`function` 与 `task` 对比：

| 对比 | `function` | `task` |
|---|---|---|
| 返回值 | 有且只有一个（函数名） | 没有返回值，靠 `output` 参数带回 |
| 能否含延时/事件 | 不能 | 可以 |
| 耗时 | 0 时间 | 可以消耗仿真时间 |
| 典型用途 | 组合计算、可综合 | testbench 激励、打印 |

## 4. 什么时候用哪个

| 需求 | 用什么 |
|---|---|
| 批量例化 N 个子模块、批量连线 | `generate for` |
| 按参数选不同结构 | `generate if / case` |
| 一段表达式在多处复用 | `function` |
| testbench 里重复的激励序列 | `task` |
| 只是简单的批量赋值 | 直接用 `always` 里的 `for` |

## 5. 本章小结

> **generate 造硬件：循环/条件生成多份结构，条件、次数必须是常量。**
> **function 是组合函数：有返回值、无延时、可综合。**
> **task 是过程任务：可有延时、可有多个输出，多用于仿真。**
> **三者都不是"软件函数调用"，硬件上都是就地展开，调用几次就有几份电路。**

---

# 14. 常用组合电路

> ⚠️ **本章是补全章节**：原笔记没有"常用组合电路"汇总章，但零散地给过多个完整组合逻辑例子（2 选 1 MUX、ALU、三八译码器、全加器、门原语实现）。本章把它们集中归类，并标注各自在原文的位置，代码一字未改。
> 补全素材来源：本笔记第 5、6、9 章 + [05A_三八译码器Verilog实现.md](../小梅哥FPGA/05A_三八译码器Verilog实现.md) + [数电中的assign.md](数电中的assign.md)。
> 组合电路的本质：**输出只取决于当前输入，没有记忆元件**（第 5 章"用数电理解 assign"已讲）。

## 1. 二选一多路器（MUX2）

**多路器就是 `?:` 或 `if/case`**，是最基本的组合电路。

赋值实现（第 5 章完整例子）：

```verilog
module mux2(
    input  wire a,
    input  wire b,
    input  wire sel,
    output wire y
);
    assign y = sel ? b : a;
endmodule
```

过程块实现（第 7 章）：

```verilog
always @(*) begin
    if (sel)
        y = a;
    else
        y = b;
end
```

对应硬件：

```text
a ──┐
    ├── MUX ──> y
b ──┘
sel ──┘
```

## 2. 门原语实现的多路器

【补全·来源：原笔记"门原语"章】

```verilog
module mux2(
    input  wire a,
    input  wire b,
    input  wire sel,
    output wire y
);

    wire sel_n;
    wire a_sel;
    wire b_sel;

    not  u_not (sel_n, sel);          // sel_n = ~sel
    and  u_and1(a_sel, a, sel_n);     // a_sel = a & ~sel
    and  u_and2(b_sel, b, sel);       // b_sel = b & sel
    or   u_or  (y, a_sel, b_sel);     // y = a_sel | b_sel

endmodule
```

逻辑：

```text
y = (a & ~sel) | (b & sel)
```

当 `sel=0`，`y=a`；当 `sel=1`，`y=b`。

## 3. 四选一多路器（由 if / case 综合）

`case` 写法（第 9 章）：

```verilog
always @(*) begin
    case (sel)
        2'b00: y = a;
        2'b01: y = b;
        2'b10: y = c;
        default: y = d;
    endcase
end
```

`if-else if` 写法（会综合成**优先级**链，注意与 case 的区别）：

```verilog
always @(*) begin
    if (sel0)
        y = a;
    else if (sel1)
        y = b;
    else if (sel2)
        y = c;
    else
        y = d;
end
```

## 4. 半加器与全加器

【补全·来源：`数电中的assign.md`】

**半加器（门原语版，原笔记"门原语"章）**

```verilog
module half_adder(
    input  wire a,
    input  wire b,
    output wire sum,
    output wire cout
);

    xor u_xor (sum, a, b);    // sum = a ^ b
    and u_and (cout, a, b);   // cout = a & b

endmodule
```

**全加器（assign 版）**

```verilog
module full_adder(
    input  wire a,
    input  wire b,
    input  wire cin,
    output wire sum,
    output wire cout
);
    assign sum  = a ^ b ^ cin;
    assign cout = (a & b) | (a & cin) | (b & cin);
endmodule
```

**多位加法器（用拼接取进位，第 5、12 章都用了它）**

```verilog
module adder8(
    input  wire [7:0] a,
    input  wire [7:0] b,
    input  wire       cin,
    output wire [7:0] sum,
    output wire       cout
);
    assign {cout, sum} = a + b + cin;
endmodule
```

## 5. 三八译码器

【补全·来源：`05A_三八译码器Verilog实现.md`】

### 5.1 原理

三八译码器有 **3 个输入端口** 和 **8 个输出端口**，8 个输出端口中的每一个端口对应三个输入端口的一种组合情况。

- 输入 `A2、A1、A0` 组成的十进制数是几，则对应编号的输出端口有效
- **低电平有效的芯片**：某位输出低电平，其余输出高电平
- **本设计采用高电平有效**：某位输出高电平，其余输出低电平（实际使用中更常见）

例如：

| A2 | A1 | A0 | 十进制值 | 有效输出 |
|----|----|----|----------|----------|
| 1  | 0  | 0  | 4        | Y4 为高（芯片版 Y4' 为低） |
| 0  | 0  | 0  | 0        | Y0 为高 |
| 0  | 1  | 1  | 3        | Y3 为高 |

核心功能：通过三个端口控制 8 个信号，但有局限性——**8 位里面每次仅有一位为有效电平，无法实现有两位及两位以上的端口同时有效**。

### 5.2 完整代码

```verilog
module decoder_3_8(
    A0, A1, A2,
    Y0, Y1, Y2, Y3, Y4, Y5, Y6, Y7
);
    input  A0, A1, A2;
    output Y0, Y1, Y2, Y3, Y4, Y5, Y6, Y7;

    reg Y0, Y1, Y2, Y3, Y4, Y5, Y6, Y7;

    always @(*) begin
        case ({A2, A1, A0})
            3'b000 : {Y0, Y1, Y2, Y3, Y4, Y5, Y6, Y7} = 8'b1000_0000;
            3'b001 : {Y0, Y1, Y2, Y3, Y4, Y5, Y6, Y7} = 8'b0100_0000;
            3'b010 : {Y0, Y1, Y2, Y3, Y4, Y5, Y6, Y7} = 8'b0010_0000;
            3'b011 : {Y0, Y1, Y2, Y3, Y4, Y5, Y6, Y7} = 8'b0001_0000;
            3'd4   : {Y0, Y1, Y2, Y3, Y4, Y5, Y6, Y7} = 8'b0000_1000;
            3'd5   : {Y0, Y1, Y2, Y3, Y4, Y5, Y6, Y7} = 8'b0000_0100;
            3'd6   : {Y0, Y1, Y2, Y3, Y4, Y5, Y6, Y7} = 8'b0000_0010;
            3'd7   : {Y0, Y1, Y2, Y3, Y4, Y5, Y6, Y7} = 8'b0000_0001;
            default: {Y0, Y1, Y2, Y3, Y4, Y5, Y6, Y7} = 8'b0000_0000;
        endcase
    end

endmodule
```

### 5.3 代码要点

1. **使用位拼接简化赋值**：原本每个分支要写 8 个赋值（`Y0=1; Y1=0; ...`），通过 `{Y0, Y1, ..., Y7}` 位拼接合并为一句。
2. **进制选择技巧**：
   - 前 4 个 case 用 **二进制**：`3'b000`、`3'b001` 等，更直观对应 `A2A1A0`
   - 后 4 个 case 用 **十进制**：`3'd4`、`3'd5` 等，因为分析时是按十进制理解
3. **default 分支**：虽然已经列完所有情况，但保留 `default` 养成良好编程习惯。

### 5.4 译码器相关的两条重要规则

> ⭐【重点·重复】**凡是在 `always`（`initial`）这种过程赋值语句中被赋值的信号，都需要定义为 `reg` 类型。** 即使该信号本质上是输出端口，只要在 `always` 块中被赋值，就必须加 `reg`（或写成 `output reg`）。这一条在第 3 章端口三要素、第 4 章 wire/reg 里已反复强调。
> 另一个高频扣分点是 **`case` 必须写 `default`**，否则综合出锁存器（第 9 章已讲）。

## 6. ALU（算术逻辑单元）

【补全·来源：原笔记第 9 章 case 完整例子】

```verilog
module alu(
    input  wire [3:0] op,
    input  wire [7:0] a,
    input  wire [7:0] b,
    output reg  [7:0] y
);

    always @(*) begin
        case (op)
            4'b0000: y = a + b;
            4'b0001: y = a - b;
            4'b0010: y = a & b;
            4'b0011: y = a | b;
            4'b0100: y = a ^ b;
            4'b0101: y = ~a;
            default: y = 8'b0;
        endcase
    end

endmodule
```

`op` 选择不同运算，综合成多路选择器加运算单元。

## 7. 比较器 / 位运算组合逻辑

关系运算符输出 1 位，本身就是比较器（第 10 章）：

```verilog
assign gt = (a > b);        // 1 位结果
assign eq = (a == b);       // 相等比较
```

按位运算组合示例（第 6 章完整例子）：

```verilog
module bitwise_demo(
    input  wire [3:0] a,
    input  wire [3:0] b,
    output wire [3:0] y_and,
    output wire [3:0] y_or,
    output wire [3:0] y_xor,
    output wire [3:0] y_not,
    output wire       y_logic_and,
    output wire       y_reduce_xor
);

    assign y_and = a & b;        // 按位与
    assign y_or  = a | b;        // 按位或
    assign y_xor = a ^ b;        // 按位异或
    assign y_not = ~a;           // 按位取反

    assign y_logic_and = a && b; // 逻辑与，结果 1 位
    assign y_reduce_xor = ^a;    // 归约异或，结果 1 位

endmodule
```

## 8. 组合电路通用写法小结

| 电路 | 推荐写法 |
|---|---|
| 2 选 1 MUX | `assign y = sel ? b : a;` |
| 多选 1 MUX | `case` + `default` |
| 优先级选择 | `if-else if` |
| 译码器 | `case` + 拼接赋值 |
| 加法器 | `{cout, sum} = a + b + cin;` |
| 比较器 | `assign gt = (a > b);` |
| 位运算/掩码 | `& \| ^ ~` |

> 写组合电路的两条铁律（重复即重点）：
> 1. **组合逻辑一律用 `always @(*)` + `=`**（别用 `<=`）；
> 2. **分支必须写全**（`else` / `default`），否则综合出锁存器。

---

# 15. 常用时序电路：触发器、寄存器、计数器、移位、分频、边沿检测

> ⚠️ **本章是补全章节**：原笔记只有零散的触发器/计数器写法与"移位寄存器"的引子。本章把它们集中成体系，并补上分频器、边沿检测。
> 素材来源：本笔记第 1、7、8、11、12 章（触发器/寄存器/计数器/移位）+ [02三天入门verilog速成.md](../三天入门Verilog俗称/02三天入门verilog速成.md) + [01三天入门verilog速成.md](../三天入门Verilog俗称/01三天入门verilog速成.md)。
> 时序电路的本质：**输出不只取决于当前输入，还取决于电路的历史状态**，所以必须有时钟边沿，必须有**记忆元件（触发器）**。

## 1. D 触发器

最基本的时序元件：**在时钟上升沿把 D 送到 Q，其余时间保持不变**。

```verilog
module DFF(clk, D, Q);
    input  clk, D;
    output reg Q;

    always @(posedge clk)
        Q <= D;
endmodule
```

【补全·来源：`01三天入门verilog速成.md`】要点：

- 当 `clk` 的**上升沿**到来时执行赋值，把 `D` 赋给 `Q`
- 输出在 `always` 里赋值，所以必须声明为 `reg`（或 `output reg`）

对应硬件：一个 D 触发器（1 位寄存器）。

## 2. 带复位的触发器

**同步复位**（复位只在时钟沿生效）：

```verilog
always @(posedge clk) begin
    if (rst)
        q <= 1'b0;
    else
        q <= d;
end
```

**异步复位**（复位立刻生效，不依赖时钟）：

```verilog
always @(posedge clk or posedge rst) begin
    if (rst)
        q <= 1'b0;
    else
        q <= d;
end
```

**低有效异步复位**（最常用）：

```verilog
always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        q <= 1'b0;
    else
        q <= d;
end
```

> ⭐【重点·重复】记忆法：**异步复位放敏感列表，同步复位放 `if` 里。** 异步复位信号进了 `@(...)` 就是异步，只在 `if` 里判断就是同步。这条在第 7 章、第 9 章、[always语句.md](always语句.md)（电赛考点）里都强调过。

**带使能的触发器**：

```verilog
always @(posedge clk) begin
    if (en)
        q <= d;
end
```

`en` 为 0 时 `q` 保持旧值。**综合出的是带使能的触发器，不是锁存器**，因为它在时钟边沿更新（时序逻辑不写 `else` 是"保持"，组合逻辑不写 `else` 才是锁存器——这是最容易混的一点）。

## 3. 寄存器（打一拍 / 多比特寄存器）

寄存器就是**一组并排的 D 触发器**：

```verilog
always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        q <= 8'd0;
    else
        q <= d;
end
```

### 3.1 打一拍（流水线寄存）

【补全·来源：`02三天入门verilog速成.md`】

```verilog
always @(posedge clk) begin
    q1 <= d;
    q2 <= q1;     // 非阻塞：q2 拿到的是旧的 q1
end
```

因为是非阻塞赋值，`q1`、`q2` 在同一个时钟沿**同时**更新，数据一拍一拍往后传，这就是**流水线**。

> 补充（原文件原话）：这种打拍方式在后续学习**亚稳态（metastability）消除**时至关重要，比如常见的"两级触发器同步器"。

### 3.2 为什么必须用非阻塞

如果用阻塞赋值写：

```verilog
always @(posedge clk) begin
    q1 = d;
    q2 = q1;   // q2 拿到的是新 q1，两拍变成一拍
end
```

`q2` 会在同一个时钟沿就取到新的 `q1`，两级寄存器被"短路"成一级。这就是第 8 章"时序逻辑必须用 `<=`"的物理原因。

## 4. 计数器

### 4.1 带使能和异步复位的计数器（原笔记写法）

```verilog
always @(posedge clk or posedge rst) begin
    if (rst)
        cnt <= 8'd0;
    else if (en)
        cnt <= cnt + 1'b1;
end
```

`en` 为 0 时，`cnt` 保持。对应硬件：带使能和异步复位的 8 位计数器（第 7 章完整例子）。

### 4.2 模 N 计数器（自动回卷）

```verilog
// 0 ~ 9 循环计数
always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        cnt <= 4'd0;
    else if (cnt == 4'd9)
        cnt <= 4'd0;
    else
        cnt <= cnt + 1'b1;
end
```

### 4.3 四位二进制加法计数器

【补全·来源：`02三天入门verilog速成.md`】

```verilog
module count4(clock, Q);
    input clock;
    output [3:0] Q;       // Q 是 4 位宽的数
    reg [3:0] Q;
    reg [3:0] Q1;         // 内部中间变量

    always @ (posedge clock)
        begin
            Q1 = Q + 1;
            Q  = Q1;
        end
endmodule
```

**功能：** 每当时钟上升沿到来，Q 加 1（自增）。

**说明：**

- `output [3:0] Q`：声明 Q 为 4 位宽输出
- 内部信号 `Q1` 是中间变量，需在使用前声明
- 内部信号声明格式：`数据类型 位宽 信号名称 [元素个数]`
- `always` 与 `assign`（若有）语句之间是**并行**执行的
- 没有 `Q1` 的写法：`Q = Q + 1;`（可直接这样写）

> 提示：上面这份计数器用的是阻塞赋值 `=`，在**同一个 always 内先算中间变量再输出**这种写法能跑通，但更规范的写法是全部用非阻塞 `<=`：
> ```verilog
> always @(posedge clock)
>     Q <= Q + 1'b1;
> ```
> ⭐【重点·重复】"时序逻辑用 `<=`"在第 8 章是硬规则，读旧代码时要注意识别这类"用阻塞赋值实现时序"的写法。

### 4.4 计数器的硬件构成

计数器 = **寄存器 + 加法器 +（可选）比较器/回卷 MUX**：

```text
        ┌──────────────┐
  +1 ──>│  加法器       │
        └──────┬───────┘
               │
        ┌──────▼───────┐
 clk ──>│  D 触发器组   │──> cnt
        └──────────────┘
```

## 5. 移位寄存器

**移位寄存器 = 一串首尾相接的触发器**，每个时钟沿数据整体挪一位。

### 5.1 串入并出（串并转换）

```verilog
reg [7:0] shift;

always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        shift <= 8'b0;
    else
        shift <= {shift[6:0], din};   // 左移，din 从低位进
end
```

【补全·来源：原笔记"拼接"章的串并转换示例】

### 5.2 并串转换（发送端常用）

```verilog
always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        shift <= 8'b0;
    else if (load)
        shift <= data;          // 并行装入
    else
        shift <= {1'b0, shift[7:1]};  // 右移，shift[0] 就是串行输出
end

assign dout = shift[0];
```

### 5.3 循环移位

用拼接实现（无移位运算符，见第 6 章）：

```verilog
shift <= {shift[6:0], shift[7]};   // 循环左移 1 位
shift <= {shift[0], shift[7:1]};   // 循环右移 1 位
```

### 5.4 移位寄存器与边沿检测的关系

把输入信号连续打几拍存进移位寄存器，就能"看到"信号的历史，从而检测上升沿/下降沿（下一节）。

## 6. 分频器

### 6.1 偶数分频（2 分频）

最简单：**每个时钟沿翻转一次**，输出频率为时钟的一半。

```verilog
always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        clk_div2 <= 1'b0;
    else
        clk_div2 <= ~clk_div2;
end
```

### 6.2 计数分频（N 分频）

用一个计数器数到 N/2 再翻转，或数到 N-1 再清零后取标志：

```verilog
// 计数到 DIV-1 后清零，产生一个周期的使能脉冲
parameter DIV = 50_000_000;   // 50 MHz -> 1 Hz

reg [25:0] cnt;

always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        cnt <= 26'd0;
    else if (cnt == DIV - 1)
        cnt <= 26'd0;
    else
        cnt <= cnt + 1'b1;
end

assign tick = (cnt == DIV - 1);   // 每 DIV 个时钟周期脉冲一次
```

要点：

- **分频器本质是计数器**，数到一半翻转就是 2 分频，数到 N 翻转就是 N 分频；
- 工程上更推荐输出**使能脉冲 tick**（单周期高电平），而不是分出来的时钟去驱动其他逻辑——后者属于"门控时钟/衍生时钟"，会带来时序与约束麻烦（见第 18 章约束）；
- 奇数分频需要"半个计数周期"的技巧（上升沿/下降沿各翻一次再相或），属于进阶用法。

> 【不常用】用 "always @(posedge clk_div)" 让分频时钟直接驱动时序逻辑，在初学者代码里常见，但**工程上不推荐**（时钟树、约束、跨时钟域都变麻烦）。推荐只分频出使能信号。

## 7. 边沿检测

边沿检测 = **把信号打一拍存住，再和当前值比较**。

### 7.1 上升沿检测

```verilog
reg d_dly;   // 上一拍的 d

always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        d_dly <= 1'b0;
    else
        d_dly <= d;
end

assign pos_edge = d & ~d_dly;   // 当前为 1，上一拍为 0
```

### 7.2 下降沿检测

```verilog
assign neg_edge = ~d & d_dly;
```

### 7.3 双边沿（任意跳变）

```verilog
assign any_edge = d ^ d_dly;    // 异或：两位不同即有跳变
```

### 7.4 为什么能检测边沿

```text
clk       ↑   ↑   ↑   ↑   ↑
d         0   0   1   1   1
d_dly     0   0   0   1   1
pos_edge  0   0   1   0   0     <- 只在 d 由 0 变 1 的那一拍为 1
```

要点：

- 边沿检测输出是**单周期脉冲**，适合做"事件触发"（如按键按下只响应一次）；
- 按键/外部异步信号进 FPGA 前，最好先**两级触发器同步**（打两拍）再检测边沿，防亚稳态；
- 检测的是"时钟采样点上的变化"，比时钟快的毛刺检测不到——那属于毛刺过滤，需要额外处理。

> 【不常用】真正意义上的"任意窄脉冲检测"需要更复杂的握手/展宽电路，入门阶段用"打一拍比较"即可。

## 8. 本章总结口诀

> **触发器：时钟沿采 D，其余时间保持不变。**
> **寄存器：一组触发器并排，非阻塞才能打拍。**
> **计数器：寄存器 + 加法器 + 回卷比较。**
> **移位寄存器：首尾相接，拼接实现。**
> **分频：本质是计数器，最好输出使能脉冲。**
> **边沿检测：打一拍再比较，`d & ~d_dly` 是上升沿。**
> **同步/异步复位：异步进敏感列表，同步放 if 里。**
> **时序不写 else 是保持，组合不写 else 是锁存器。**

---

# 16. 状态机

> ⚠️ **本章是补全章节**：原笔记的状态机内容分散在第 7 章（计数器式状态更新）、第 9 章（`case` 版 FSM 完整例子）[always语句.md](always语句.md) 的 case 状态机片段中，第 16 章原本只有空标题。本章把它们收拢，并补齐"三段式写法 + 状态编码"。
> 素材来源：本笔记第 9 章 FSM 完整例子、[always语句.md](always语句.md) 的 case 例子，以及同目录的 [状态机.md](状态机.md)（状态机专项笔记）。

## 1. 状态机是什么

状态机（FSM，Finite State Machine）就是"**用一组寄存器记住当前处于哪个状态，再根据输入决定下一个状态和输出**"的电路。它本质上是：

```text
当前状态（寄存器） + 输入  ->  下一个状态（组合逻辑）  ->  输出（组合逻辑）
```

在 Verilog 里，状态机几乎总是用 `case` + `always` 写出来（第 9 章已给出一个完整例子）。

## 2. 两段式（原笔记写法）

```verilog
module fsm(
    input  wire clk,
    input  wire rst_n,
    input  wire start,
    input  wire done,
    output reg  busy
);

    localparam IDLE = 2'b00;
    localparam RUN  = 2'b01;
    localparam DONE = 2'b10;

    reg [1:0] state, next_state;

    // 状态寄存器（时序）
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= IDLE;
        else
            state <= next_state;
    end

    // 下一状态组合逻辑
    always @(*) begin
        case (state)
            IDLE: next_state = start ? RUN : IDLE;
            RUN:  next_state = done  ? DONE : RUN;
            DONE: next_state = IDLE;
            default: next_state = IDLE;
        endcase
    end

    // 输出逻辑
    always @(*) begin
        case (state)
            IDLE: busy = 1'b0;
            RUN:  busy = 1'b1;
            DONE: busy = 1'b0;
            default: busy = 1'b0;
        endcase
    end

endmodule
```

## 3. 三段式写法（推荐）

工程上更规范的是**三段式**：一段时序（状态寄存器）、一段组合（下一状态）、一段输出（组合或时序）。

```verilog
module fsm_3seg(
    input  wire clk,
    input  wire rst_n,
    input  wire start,
    input  wire done,
    output reg  busy
);

    // 1) 状态编码
    localparam IDLE = 2'b00;
    localparam RUN  = 2'b01;
    localparam DONE = 2'b10;

    reg [1:0] state, next_state;

    // 2) 第一段：状态寄存器（时序，非阻塞）
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= IDLE;
        else
            state <= next_state;
    end

    // 3) 第二段：下一状态组合逻辑（组合，阻塞，分支写全）
    always @(*) begin
        case (state)
            IDLE:    next_state = start ? RUN  : IDLE;
            RUN:     next_state = done  ? DONE : RUN;
            DONE:    next_state = IDLE;
            default: next_state = IDLE;
        endcase
    end

    // 4) 第三段：输出逻辑（组合）
    always @(*) begin
        case (state)
            IDLE:    busy = 1'b0;
            RUN:     busy = 1'b1;
            DONE:    busy = 1'b0;
            default: busy = 1'b0;
        endcase
    end

endmodule
```

三段式的好处：

- 时序部分只有状态寄存，**不会误综合出锁存器**；
- 组合部分集中写下一状态，分支是否写全一目了然；
- 输出逻辑独立，便于改成时序输出（消除组合毛刺）。

## 4. Moore 型与 Mealy 型

| 类型 | 输出取决于什么 | 特点 |
|---|---|---|
| Moore 型 | 只取决于**当前状态** | 输出稳定，晚一拍 |
| Mealy 型 | 取决于**当前状态 + 输入** | 响应快，可能有组合毛刺 |

上面的例子是 Moore 型（`busy` 只看 `state`）。若改成 Mealy 型，输出条件里加上输入：

```verilog
always @(*) begin
    case (state)
        IDLE: busy = start;      // 输入直接进输出
        RUN:  busy = 1'b1;
        DONE: busy = 1'b0;
        default: busy = 1'b0;
    endcase
end
```

> 【不常用/进阶】输出直接由组合逻辑给出的 Mealy 输出可能带毛刺，对时序敏感的设计会把第三段也写成时序输出（寄存一拍）。

## 5. 状态编码方式

| 编码 | 说明 | 特点 |
|---|---|---|
| 二进制编码 | `2'b00`、`2'b01`… | 触发器最少，译码逻辑多 |
| 独热码（one-hot） | 每个状态 1 位，如 `4'b0001` | 触发器多，译码逻辑少，FPGA 上时序更好 |
| 格雷码 | 相邻状态只变 1 位 | 降低翻转功耗、减少毛刺 |

FPGA 里综合工具常会自动选独热码；手写时用 `localparam` 明确编码即可。

## 6. 状态机设计要点（重复即重点）

> ⭐【重点·重复】以下每一条都在前面章节讲过，状态机是它们的集中体现：

1. **状态寄存器用 `always @(posedge clk or negedge rst_n)` + `<=`**（第 7、8、15 章）；
2. **下一状态用 `always @(*)` + `=`，且 `case` 必须有 `default`**（第 7、9 章）；
3. **一个 reg 只能在一个 always 里赋值**（第 7、20 章）；
4. **状态编码用 `localparam`，不要用魔法数字**（第 11 章）；
5. **复位后必须能回到一个确定的初始状态**（第 7、15 章）；
6. **不要有无法到达的状态或死循环**（`default` 兜底）。

## 7. 本章小结

> **状态机 = 状态寄存器 + 下一状态组合逻辑 + 输出逻辑。**
> **推荐三段式：时序存状态、组合算次态、独立写输出。**
> **状态用 `localparam` 命名，`case` 必带 `default`。**
> **Moore 输出稳、Mealy 响应快。**

---

# 17. Testbench 仿真

> ⚠️ **本章是补全章节**：原笔记第 15 章只有空标题。素材来自 [03B_仿真验证.md](../小梅哥FPGA/03B_仿真验证.md)（Gowin + ModelSim 联合仿真流程）与 [端口.md](端口.md)（testbench 不需要端口列表）、[wire和reg的对比.md](wire和reg的对比.md)（testbench 里 reg/wire 的分工）。

## 1. 仿真的本质

所谓仿真 = **给输入端口加激励信号 → 观察输出端口的信号波形**。

- 需要的工具：专门的仿真软件（如 ModelSim、Vivado 自带仿真器）
- 需要的平台：Testbench（测试平台）

### FPGA 验证的两大阶段

| 阶段 | 名称 | 含义 |
|------|------|------|
| 前仿真 | 理论功能验证 / 功能仿真 | 不涉及具体硬件延时，仅验证逻辑功能是否符合预期 |
| 后仿真 | 实际实现的验证 | 在真实硬件上验证，包含门级延时信息 |

初学阶段重点做**前仿真**。

### Testbench 的类比

将 Testbench 想象成一张实验桌：

- 桌子上放着**被测试模块**（DUT，Device Under Test）
- 桌上有**信号发生器**（产生激励信号）
- 桌上有**示波器/逻辑分析仪**（观察输出波形）
- 通过**导线**把所有仪器和模块连接起来

Testbench 本身也是一份 **Verilog 代码**，但**仅在仿真软件中执行，不会在 FPGA 芯片上综合成实际电路**，因此编写时可以使用的语法更灵活（可以用 `#` 延时、`initial`、`$display` 等——这些都属于第 19 章的"不可综合"语法）。

## 2. Testbench 文件编写步骤

### 2.1 新建文件与命名

- File → New → Verilog File
- 文件命名：`mux2_tb.v`
  - `mux2`：与被测试模块同名
  - `tb`：`testbench` 的缩写（行业通用命名约定，**仅用于提示阅读者，非软件强制要求**）
  - 中间的 `_` 是**下划线**（英文输入下 Shift + 减号），Verilog 中连字符 `-` 是减号运算符
- 存放路径：工程的 `src` 目录下

### 2.2 第一行固定代码：`timescale

```verilog
`timescale 1ns / 1ns
```

> 注意第一个撇号是**键盘左上角**的撇号（数字 1 左边），不是回车键旁边的撇号。

- 语法作用，保留字
- 含义：声明仿真中**延时语句的时间单位 / 仿真精度**
  - 前面 `1ns`：延时单位
  - 后面 `1ns`：仿真精度（最小时间刻度）
- 例如：`#20` 表示延时 20ns
- 若写成 `1ns/1ps`，则 `#20.1` 表示 20.1ns，`#20.001` 表示 20.001ns（最多小数点后三位）

### 2.3 模块声明与例化（DUT 放置）

```verilog
module mux2_tb();

    // ① 把被测试模块放到平台上（例化）
    mux2 mux2 (
            // 后面再写端口连接
        );

endmodule
```

要点：

- TB 文件**不需要端口列表**，括号可写可不写（原因见第 3 章"为什么仿真的时候不用写端口列表"）
- `module` / `endmodule` 表示代码起止，与设计文件一致

### 2.4 例化（DUT 标签贴纸）

将设计源文件中模块名+端口列表粘贴进来，这就是**把模块放到测试桌上**。

**为什么要"贴标签"？**
当桌上有**多个一模一样的模块**时，需要用标签区分它们，否则会冲突。

```verilog
mux2 mux2 (   // 第一个 mux2 是模块名，第二个 mux2 是给本实例起的标签
    .A(),
    .B(),
    .S0(),
    .out()
);
```

- 标签名随意：`mux2_a`、`mux2_b`、`mux2_666` 都行
- 只要标签名之间不冲突即可

> **重要提醒**：常见错误是把"被测模块输入端口在 TB 中定义为 reg、输出端口定义为 wire"误以为是一种固定死板语法。实际上：
> - 当同时例化**两个相同模块**时，如果它们的 out 都连到同一个 `wire`，会因为**多驱动源**报错
> - 正确做法：定义两个独立的 wire 信号，分别接到两个实例的 out 端口

### 2.5 定义激励信号与观测信号（接导线）

```verilog
// 信号发生器：三个可随时修改的激励信号
reg  S0;
reg  S1;
reg  S2;

// 示波器/逻辑分析仪：观测 DUT 输出
wire mux2_out;
```

- `reg`：激励信号需要被赋值（驱动源），用 `reg`
- `wire`：观测 DUT 输出，不能驱动它，用 `wire`

> ⭐【重点·重复】"testbench 里激励用 reg、观测用 wire"在第 4 章（wire/reg 选择表）已出现，此处是同一规则的仿真侧应用。

**端口连接**（用导线/一端连接起来）：

```verilog
mux2 mux2 (
    .A   (S0),     // 信号发生器 S0 接到 DUT 的 A 端口
    .B   (S1),     // S1 接到 B
    .S0  (S2),     // S2 接到 S0（即 sel）
    .out (mux2_out)
);
```

> 注意这里 S2 接的是被测模块的 S0（选择端），被测模块的 S0 对应本节设计的"二选一选择端"。

## 3. 编写激励：initial 块

```verilog
initial begin
    S2 = 0; S1 = 0; S0 = 0;     // 时刻 0：三个信号都为 0
    #20;                        // 时间向后推移 20ns（此期间信号保持不变）

    S2 = 0; S1 = 0; S0 = 1;     // 20ns：S0 变为 1
    #20;

    S2 = 0; S1 = 1; S0 = 0;     // 40ns
    #20;

    S2 = 0; S1 = 1; S0 = 1;     // 60ns
    #20;

    S2 = 1; S1 = 0; S0 = 0;     // 80ns
    #20;

    S2 = 1; S1 = 0; S0 = 1;     // 100ns
    #20;

    S2 = 1; S1 = 1; S0 = 0;     // 120ns
    #20;

    S2 = 1; S1 = 1; S0 = 1;     // 140ns
    #20;

    $stop;                      // 结束仿真
end
```

关键语法说明：

| 语法 | 作用 |
|------|------|
| `initial` | 初始化语句，与 begin/end 配对使用 |
| `begin ... end` | initial 块的内容 |
| 在 initial 块中对 reg 信号直接 `S0 = xxx;` | 顺序阻塞赋值，每条语句用 `;` 隔开 |
| `#20` | 在仿真时间轴上向后推移 20 个单位（单位由 timescale 决定） |
| `#延时` | **仅用于仿真**，不能用于可综合的 RTL 代码（FPGA 内部没有"延时"的硬件结构） |
| `$stop` | 暂停仿真 |
| `$finish` | 结束仿真（另一种常见收尾） |
| `$display` | 在控制台打印（常用于打印中间值） |

完整 8 例 mux2_tb.v：

```verilog
`timescale 1ns / 1ns

module mux2_tb();

    reg  S0;
    reg  S1;
    reg  S2;
    wire mux2_out;

    mux2 mux2 (
        .A   (S0),
        .B   (S1),
        .S0  (S2),
        .out (mux2_out)
    );

    initial begin
        S2 = 0; S1 = 0; S0 = 0;   #20;
        S2 = 0; S1 = 0; S0 = 1;   #20;
        S2 = 0; S1 = 1; S0 = 0;   #20;
        S2 = 0; S1 = 1; S0 = 1;   #20;
        S2 = 1; S1 = 0; S0 = 0;   #20;
        S2 = 1; S1 = 0; S0 = 1;   #20;
        S2 = 1; S1 = 1; S0 = 0;   #20;
        S2 = 1; S1 = 1; S0 = 1;   #20;
        $stop;
    end

endmodule
```

> 激励覆盖了 S2/S1/S0 的全部 8 种组合，每隔 20ns 切换一次状态，便于观察输出响应。

## 4. 产生时钟与复位

【补全·来源：`wire和reg的对比.md`、[端口.md](端口.md)】

### 4.1 时钟

```verilog
reg clk = 0;
always #5 clk = ~clk;      // 周期 10ns（100MHz）的时钟
```

或用 `forever`：

```verilog
initial begin
    clk = 0;
    forever #5 clk = ~clk;
end
```

### 4.2 复位

```verilog
initial begin
    rst_n = 0;
    #20 rst_n = 1;
end
```

### 4.3 完整的最小 testbench 框架

```verilog
`timescale 1ns / 1ns

module top_tb();

    reg  clk;
    reg  rst_n;
    reg  [7:0] din;
    wire [7:0] dout;

    // DUT 例化
    top u_top(
        .clk   (clk),
        .rst_n (rst_n),
        .din   (din),
        .dout  (dout)
    );

    // 时钟
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    // 复位与激励
    initial begin
        rst_n = 0;
        din   = 8'd0;
        #20;
        rst_n = 1;
        #20;
        din = 8'd5;  #20;
        din = 8'd10; #20;
        $finish;
    end

endmodule
```

> `always #5 clk = ~clk;` 属于"仿真专用 always"，**不可综合**（见第 19 章）。它是 `always` 的第三种用法（[always语句.md](always语句.md) 的速记里单列过）。

## 5. ModelSim 与 Gowin 联合仿真流程

【补全·来源：`03B_仿真验证.md`】

高云 Gowin 软件**未集成仿真器**，需要使用第三方工具。以下使用 **ModelSim**。

### 5.1 在 ModelSim 中新建工程

- File → New → Project
- 填写：
  - **Project Name**：`mux2`（建议与 FPGA 工程同名）
  - **Project Location**：浏览到设计工程目录下，新建 `sim` 文件夹作为路径
- 点击 OK

### 5.2 添加已有文件

弹出对话框选择后续操作，选 **Add existing file**（添加已有文件）：

- 点击 Browse
- 同时添加设计文件 `mux2.v` 和仿真文件 `mux2_tb.v`
- 添加完成后关闭此页面

### 5.3 编译

- Compile → Compile All
- 文件状态由 ❓ 变为 ✔ 即编译通过
- 下方 Transcript 窗口会显示编译成功 / 报错信息
- **编译必须通过且无警告**，否则需修改后重新编译

### 5.4 配置仿真环境

- 右键点击 → **Add to Project** → **Simulation Configuration**
- 设置：
  - **Design** 下选择 `work` 库 → `mux2_tb` 作为仿真顶层
  - 仿真配置名称：复制仿真模块名 `mux2_tb`
  - 点击 **Optimization Options**
  - 勾选 **Apply for visibility to module**（**必须勾选**，否则不会出现正常波形图）
- 点击 Save 保存

### 5.5 运行仿真

- 双击 project 栏中的 `mux2_tb` 仿真配置，进入波形界面
- 在信号列表中选择需要观察的模块/信号 → 右键 → **Add Wave**
- 点击工具栏 **Run**（运行仿真）
- 即可看到波形输出

## 6. 波形验证

点击放大镜查看全局波形，对照设计预期：

| S2（S0 端） | 输出行为 | 波形验证 |
|-------------|----------|----------|
| `S2 = 0` | `out = A = S0` | 输出波形跟随 S0，与 S1 无关 |
| `S2 = 1` | `out = B = S1` | 输出波形跟随 S1，与 S0 无关 |

- 在 S2=0 的时间段内，S0 变化时输出同步变化；S1 变化时输出不变
- 在 S2=1 的时间段内，S1 变化时输出同步变化；S0 变化时输出不变

**两条分支都被验证符合设计预期 → 仿真验证成功。**

## 7. 常见问题与学习建议

【补全·来源：`03B_仿真验证.md`】

- 操作不熟练、代码语法错误会导致结果不一致或出不来波形 → 跟视频重做，逐步核对
- 找不到问题原因可联系售后技术同事
- 课程学习建议：不熟悉流程时，重复操作 2~3 遍，在做的过程中逐步理解每个环节
- 下一步：在开发板上进行**实测**（板级验证）

## 8. 本章小结

> **仿真 = 加激励 + 看波形。**
> **testbench 不需要端口列表，`timescale` 定单位和精度。**
> **激励信号用 `reg`，观测信号用 `wire`。**
> **`#延时`、`initial`、`$stop`、`always #5 clk=~clk` 都只在仿真里用。**
> **流程：建工程 → 加设计文件+TB → 编译 → 设仿真顶层 → Run → Add Wave 看波形。**

---

# 18. 开发流程与约束

> ⚠️ **本章是补全章节**：原笔记第 18 章原为"开发流程与工具"，只有空标题。
> 素材来源：[03A_Verilog输入.md](../小梅哥FPGA/03A_Verilog输入.md)（建工程、设计输入、语法检查、综合）、[03B_仿真验证.md](../小梅哥FPGA/03B_仿真验证.md)（仿真环节）、[05A_三八译码器Verilog实现.md](../小梅哥FPGA/05A_三八译码器Verilog实现.md)（综合与 RTL 视图）。

## 1. 完整开发流程

```text
① 创建工程（选器件）
      ↓
② 设计输入（写 Verilog）
      ↓
③ 语法检查（RTL Analysis）
      ↓
④ 综合 Synthesis
      ↓
⑤ 查看 RTL 视图（确认电路结构对不对）
      ↓
⑥ 功能仿真（Testbench，见第 17 章）
      ↓
⑦ 约束（引脚约束 / 时序约束）
      ↓
⑧ 布局布线 Place & Route
      ↓
⑨ 生成比特流 → 下载到 FPGA → 板级实测
```

## 2. 创建工程

【补全·来源：`03A_Verilog输入.md`】

- **开发板**：ACG720 或 ACG750（二者硬件资源相同，仅封装引脚不同）
- **FPGA 芯片型号**：`GW5AT-LV138PG484AC1/I0`
  - 另有 60K 版本：`GW5AT-LV60PG484AC1/I0`
  - 通过芯片丝印判断版本号（型号下一行的字母，如 `2404B` 中的 `B` 即为版本号）
- **开发软件**：Gowin，版本 `1.9.12`

### 2.1 打开 Gowin 软件

启动后界面分为四栏：

| 栏位 | 含义 |
|---|---|
| Recent Project | 近期打开过的工程 |
| Quick Start | 快速开始（New Project / Open Project / Open Example Project） |
| Tools | 工具集合（Flow Planner 物理约束、Timing Constraints Editor 时序约束、Programmer 下载等） |
| User Manuals | 用户手册链接到高云官网 |

### 2.2 新建工程步骤

1. 点击 **New Project** → 弹出对话框 → 选择 **FPGA Design Project** → OK
2. 进入 **Project Name** 页：
   - 工程名 `Name`：输入 `mux2to1`（命名要有实际意义）
   - 路径 `Create in`：选择工程存放目录
   - 勾选 `Used as default project location`（下次建工程默认此路径，可按需选择）

> **注意事项**：
> - 工程名不能含中文和空格，否则流程会报错
> - 路径不能过长：Windows 限制 260 字符，Linux 限制 4096 字符

3. 进入 **Select Device** 页（关键步骤）：
   - Device：选择芯片具体型号
   - 选 `GW5AT-LV138PG484AC1/I0`，Version 选 `B`
   - 若使用 60K 版本，则改为 `GW5AT-LV60PG484AC1/I0`
4. 进入 **Summary** 页：核对所有设置，点击 **Finish** 完成工程创建。

> **创建工程三步总结**：指定路径 → 选择器件 → 完成。

## 3. 设计输入

### 3.1 新建 Verilog 源文件

1. 菜单栏 **File → New**（或快捷键 `Ctrl + N`）
2. 在弹出的选项卡中选择 **Verilog File**（在 Files 分类下）
3. 命名：与工程名保持一致，输入 `mux2to1` → OK

### 3.2 代码结构要点

任意 Verilog 模块都以 `module` 关键字开始，以 `endmodule` 结束。模块名紧跟 `module` 之后。

- 端口列表写在 `module 模块名(...)` 后的括号中，以 **逗号** 分隔，最后一个端口后 **无逗号**
- 括号结束必须紧跟 **分号 `;`**
- 输入信号用 `input` 声明，输出信号用 `output` 声明
- 每个端口声明后用 **分号 `;`** 结尾（不再是逗号）

**Verilog 语法细节**：

- **大小写敏感**：大写 `A` 与小写 `a` 是两个不同信号
- **字符必须为英文**：所有标点（逗号、分号、括号、冒号、问号）都不能使用中文符号
- **连续赋值语句**：使用 `assign` 关键字，对 wire 类型信号赋值

> 这三条是初学者最常犯的低级错误（中文分号、大小写、缺分号），务必逐条检查。

## 4. 语法检查、综合与 RTL 视图

【补全·来源：`03A_Verilog输入.md`、`05A_三八译码器Verilog实现.md`】

### 4.1 语法检查

按 `Ctrl + S` 保存文件后，切换到 **Hierarchy（层次结构）** 界面：

- 若代码有语法错误，会在窗口顶部以 **红色字体** 显示 `RTL Analysis Error`，并指出错误所在行
- 故意将英文分号 `;` 改为中文分号 `；` 后保存，会触发该错误提示；改回英文分号后错误消失

### 4.2 综合（Synthesis）

在 **Process** 界面，双击 **Synthesize** 按钮，软件会对代码进行分析与综合。

### 4.3 查看 RTL 视图

综合完成后：

1. 点击 **Tools → Schematic Viewer → RTL Design View**
2. 即可看到电路模型图

**观察要点（以二选一多路器为例）**：

- 电路图与手绘的二选一多路器符号图基本一致
- `sel` 信号后面会自动接一个 **非门（取反）**
- 当 `sel == 0` 时，经非门变为 `1`，输出 `a` 的值
- 当 `sel == 1` 时，经非门变为 `0`，输出 `b` 的值
- 综合后的电路与功能预期一致

> 三八译码器的 RTL 视图：它属于较复杂的数字逻辑基本单元，软件没有现成的 38 译码器模型，因此会将内部结构分解展示，原理图不像二选一多路器那样有明显的典型特征。

## 5. 约束（Constraint）

约束告诉工具两件事：**哪个信号接到哪个物理引脚**（引脚约束）、**电路要跑到多快**（时序约束）。

### 5.1 引脚约束（物理约束）

每个对外端口都要映射到芯片的具体引脚，通常由 `.cst`（Gowin）/ `.xdc`（Xilinx）文件或 GUI 的 **Flow Planner** 完成。例如 Gowin 物理约束文件（`.cst`）的写法形如：

```text
IO_LOC "clk" 52;
IO_LOC "rst_n" 53;
IO_LOC "led[0]" 10;
IO_PORT "clk" IO_TYPE=LVCMOS33 PULL_MODE=UP;
```

要点：

- 引脚号必须查开发板原理图/手册，**不能凭猜**；
- 时钟引脚要选支持全局时钟网络的引脚；
- 未约束的端口会被工具自动分配，可能"能下载但不工作"。

### 5.2 时序约束

告诉工具时钟周期（频率），工具据此做时序分析（建立/保持时间）。Gowin 用 **Timing Constraints Editor**（`.sdc` 风格）：

```text
create_clock -name clk -period 20 -waveform {0 10} [get_ports {clk}]
```

表示 `clk` 周期 20ns（50MHz）。

要点：

- **时钟频率决定了时序收敛的难度**，先跑通功能，再逐步提频；
- 用分频时钟去驱动逻辑（第 15 章"不推荐"那条）会让时序约束变复杂，所以更推荐输出**使能脉冲**而不是衍生时钟；
- 跨时钟域信号必须先做同步（两级触发器），否则时序分析不覆盖、功能也不可靠。

### 5.3 约束与可综合性无关

注意区分：

| 概念 | 含义 |
|---|---|
| 可综合 | 代码能否转成电路（第 19 章） |
| 约束 | 电路映射到哪个引脚、跑多快 |

**约束文件本身不是 Verilog**，也不是"不可综合的 Verilog"，而是给工具的实现指令。

## 6. 下载与实测

流程的最后一步：生成比特流（bitstream）→ 用 Programmer 下载到 FPGA → 在开发板上实测。

- 仿真通过 ≠ 板上一定对：还要考虑引脚、时钟、复位电平、按键抖动等实际因素；
- 板级调试常用手段：点灯（LED 指示状态）、逻辑分析仪（Gowin 的在线逻辑分析）、`$display`（仅仿真）。

## 7. 本章小结

> **流程：建工程 → 写代码 → 语法检查 → 综合 → 看 RTL → 仿真 → 约束 → 布局布线 → 下载实测。**
> **工程名别用中文/空格，路径别太长。**
> **标点必须是英文，Verilog 大小写敏感。**
> **约束管"接哪个脚、跑多快"，和可综合性是两件事。**
> **先功能后性能：先让逻辑对，再提时钟频率。**

---

# 19. 可综合与不可综合

> ⚠️ **本章是补全章节**：原笔记第 20 章（原文编号）只有空标题，但"可综合/不可综合"的判断散落在第 5 章（assign 延迟）、第 7 章（always 能写什么）、第 11 章（数据类型可综合性表）中。本章把它们汇总成清单。

## 1. 什么叫"可综合"

**综合（Synthesis）** = 把 Verilog 代码翻译成门级网表/电路。
**可综合** = 这段代码能被综合工具翻译成真实电路。
**不可综合** = 这段代码只在仿真器里有意义，综合工具无法（或不应）把它变成硬件。

一句话判断法：

> **这句话描述的是"硬件结构"还是"仿真过程"？**
> 描述硬件 → 可综合；描述仿真过程（时间、打印、文件）→ 不可综合。

## 2. 可综合的语法清单

| 类别 | 可综合写法 |
|---|---|
| 模块 | `module` / `endmodule`、端口声明、例化 |
| 连线 | `assign` 连续赋值 |
| 过程块 | `always @(*)`、`always @(posedge clk ...)` |
| 分支 | `if / else`、`case / casez` |
| 循环 | `for`（循环次数为常量，展开成硬件）、`generate for` |
| 算子 | 算术、关系、相等、逻辑、按位、归约、移位、拼接、条件运算符 |
| 类型 | `wire`、`reg`、`logic`、`parameter`、`localparam`、`integer`（循环用） |
| 数组 | `reg [7:0] mem [0:255]`（可映射为 RAM/ROM，取决于写法） |
| 函数 | `function`（纯组合、无延时） |

## 3. 不可综合或需谨慎的语法清单

| 类别 | 不可综合/危险写法 | 说明 |
|---|---|---|
| 延时 | `#5`（`assign #5`、`#5 q<=d`、门原语延迟） | 只用于仿真，综合忽略或报错 |
| 过程块 | `initial` | 只在仿真里执行一次；FPGA 上可用作上电初值，但**不能**当作可靠复位 |
| 时间控制 | `@`、`wait`、`forever`（除 `always #5 clk=~clk` 这类仿真时钟） | 仿真专用 |
| 时钟产生 | `always #5 clk = ~clk;` | 仅 testbench |
| 系统任务 | `$display`、`$stop`、`$finish`、`$monitor`、`$dumpfile` | 仅仿真/调试 |
| 类型 | `real`、`realtime`、`time`、`event`、`string` | 仿真 |
| 系统函数 | `$random`、`$time`（多数） | 仿真 |
| 运算符 | `**`（幂） | 一般不可综合，慎用 |
| 相等 | `===`、`!==` | 精确比较，主要用于仿真 |
| 循环 | `while`、次数非常量的 `for` | 一般不综合（次数必须是常量） |
| 延迟与事件 | `fork...join` | 不可综合 |
| 编译指令 | `` `include ``、`` `define ``（本身可综合，但要注意路径/展开） | 属于预处理 |

## 4. 容易踩的"半可综合"陷阱

这几条不是"语法不可综合"，而是**语法能过、但综合结果不是你想要的**，比纯不可综合更危险：

1. **组合逻辑分支不全 → 意外锁存器**
   ```verilog
   always @(*) begin
       if (en) y = a;    // 少了 else，综合出 latch
   end
   ```
   ⭐【重点·重复】第 7、9、20 章反复强调。

2. **时序逻辑用阻塞赋值 → 打拍失效**
   ```verilog
   always @(posedge clk) begin
       q1 = d;  q2 = q1;   // 应是 <=，否则两级变一级
   end
   ```
   ⭐ 见第 8、15 章。

3. **同一 reg 在多个 always 里赋值 → 多驱动，报错**
   ⭐ 见第 7、20 章。

4. **依赖 `initial` 给寄存器赋初值 → 换器件/上电时序就废**
   FPGA 上电时寄存器初值取决于器件，ASIC 里根本没有；可靠做法是用**复位**。

5. **用分频时钟直接当时钟 → 时序分析困难**
   见第 15、18 章，推荐用使能脉冲。

6. **位宽隐式扩展/截断 → 仿真对、综合错**
   ⭐ 见第 6、10、11 章。

## 5. 一张表总结

| 场景 | 判断 |
|---|---|
| `assign` 表达式 | 可综合 |
| `always @(*)` + `if/case`（分支写全） | 可综合 |
| `always @(posedge clk)` + `<=` | 可综合 |
| `for`（常量次数） | 可综合，展开成硬件 |
| `#` 延时 | 不可综合（仿真） |
| `initial` | 仿真可执行；不能代替复位 |
| `$display/$stop/$finish` | 不可综合（仿真） |
| `real/time/event/string` | 不可综合（仿真） |
| `===` / `!==` | 一般不可综合 |
| `**` | 一般不可综合 |

## 6. 本章小结

> **判断标准：描述硬件 → 可综合；描述仿真过程 → 不可综合。**
> **`#延时`、`initial`、系统任务、`real/time` 只属于仿真。**
> **最危险的不是"不可综合"，而是"能综合但不是你想要的"——锁存器、打拍失效、多驱动、位宽截断。**
> **RTL 要有复位，不要依赖 `initial` 赋初值。**

---

# 20. 常见错误与代码风格

> ⚠️ **本章是补全章节**：原笔记的"常见错误"分散在各章末尾。本章把全篇所有 `常见错误` 小节汇总成清单，并给出代码风格建议。
> **这一章是"重复即重点"的集中体现**——下面每一条都在前面章节出现过至少一次，能全部避开，Verilog 就基本入门了。

## 1. 常见错误总清单

### 1.1 组合逻辑相关

| 错误 | 后果 | 正确做法 | 详见 |
|---|---|---|---|
| `always @(*)` 里 `if` 没有 `else` | 综合出锁存器 latch | 补 `else` 或先用默认值 | 第 7、9、19 章 |
| `case` 没有 `default` 且分支不全 | 综合出锁存器 | 补 `default` | 第 9 章 |
| 组合逻辑用 `<=` | 仿真竞争、结果不确定 | 组合用 `=` | 第 7、8 章 |
| 敏感列表手写成 `@(a)` 漏信号 | 仿真与综合不一致 | 一律用 `@(*)` | 第 7、9 章 |

### 1.2 时序逻辑相关

| 错误 | 后果 | 正确做法 | 详见 |
|---|---|---|---|
| 时序逻辑用 `=` | 打拍失效、仿真综合不一致 | 时序用 `<=` | 第 8、15 章 |
| 同一个 `always` 里混用 `=` 和 `<=` | 行为不可预期 | 一个 always 只用一种 | 第 8、9 章 |
| 同一个 `reg` 在多个 `always` 里赋值 | 多驱动，编译报错 | 一个 reg 只在一个 always 里赋值 | 第 7 章 |
| 异步复位信号没放进敏感列表 | 复位不同步/不生效 | `@(posedge clk or negedge rst_n)` | 第 7、15 章 |
| 靠 `initial` 给寄存器赋初值当复位 | 上电状态不确定 | 用复位逻辑 | 第 19 章 |

### 1.3 赋值与驱动相关

| 错误 | 后果 | 正确做法 | 详见 |
|---|---|---|---|
| `reg y; assign y = ...;` | 编译错误 | `assign` 左边只能是 wire | 第 4、5 章 |
| `wire y; always @(*) y = ...;` | 编译错误 | 过程赋值左边要是 reg/logic | 第 4 章 |
| 多驱动同一根 wire（两个 `assign`） | 冲突/短路 | 三态或改设计 | 第 5 章 |
| 输出端口接了 `reg` 或表达式 | 编译错误 | 输出接 wire | 第 12 章 |
| 实例名重复 | 编译错误 | 实例名唯一 | 第 12 章 |
| 端口名拼错/位置映射顺序错 | 编译过但功能错 | 用按名称映射 | 第 12 章 |
| `input` 声明成 `reg`、`inout` 用 `reg` | 编译错误 | input/inout 只能 wire | 第 3 章 |

### 1.4 位宽与数值相关

| 错误 | 后果 | 正确做法 | 详见 |
|---|---|---|---|
| 常量不写位宽（`a + 1`） | 默认 32 位，结果位宽异常 | 写 `a + 1'b1` | 第 10、11 章 |
| 位宽不够被截断（`4'd16` 得 0） | 数值错误 | 位宽算够 | 第 11 章 |
| 左移丢高位（`wire [3:0] y = a << 1;`） | 数据丢失 | 先扩展位宽或加括号 | 第 6 章 |
| 有符号/无符号混合运算 | 符号位丢失 | 显式 `$signed`/`$unsigned` | 第 10、11 章 |
| 表达式优先级把握不准 | 逻辑错 | 加括号 | 第 10 章 |
| 非 ANSI 风格漏写方向/类型 | 默认 `inout`/`wire` 出错 | 用 ANSI 风格写清楚 | 第 2、3 章 |

### 1.5 语法与书写相关

| 错误 | 后果 | 正确做法 | 详见 |
|---|---|---|---|
| 用了中文标点（`；`、`，`） | RTL Analysis Error | 全部用英文标点 | 第 18 章 |
| 大小写混用信号名 | 认为是两个信号 | 严格一致 | 第 18 章 |
| 忘记 `endcase` / `endmodule` | 编译错误 | 配对检查 | 第 9 章 |
| `case` 分支重复 | 第一个优先，容易出错 | 分支互斥 | 第 9 章 |
| 工程名含中文/空格、路径过长 | 流程报错 | 英文短路径 | 第 18 章 |

## 2. 代码风格建议

### 2.1 命名

| 对象 | 建议 | 例子 |
|---|---|---|
| 模块名 | 小写 + 下划线，与文件名一致 | `mux2to1.v` / `module mux2to1` |
| 信号名 | 小写 + 下划线，见名知义 | `data_in`、`data_out` |
| 时钟/复位 | `clk`、`rst_n`（低有效加 `_n`） | `clk`、`rst_n` |
| 低有效信号 | 统一加 `_n` 后缀 | `cs_n`、`we_n` |
| 实例名 | `u_` 前缀 | `u_sub`、`u_dff0` |
| 参数 | 全大写 | `WIDTH`、`DEPTH` |
| 状态常量 | `localparam` 全大写 | `IDLE`、`RUN` |

### 2.2 结构

- **一个文件一个模块**，文件名与模块名一致（第 2 章）；
- **一律用 ANSI 风格端口声明**（第 2、3 章）；
- **一律用按名称端口映射**（第 12 章）；
- **组合逻辑用 `assign`（简单）或 `always @(*)` + `=`（复杂）；时序逻辑用 `always @(posedge clk)` + `<=`**（第 5、7、8 章）；
- **一个 always 只描述一种逻辑、一个信号只在一个 always 里赋值**（第 7 章）；
- **状态机用三段式 + `localparam` 编码**（第 16 章）；
- **模块端口顺序建议：时钟、复位、输入、输出**；
- **不要用魔法数字**，常量写成 `localparam` 或带位宽的常量（第 11 章）。

### 2.3 可读性

- **关键逻辑加注释**，尤其是"为什么"；
- **对齐缩进**，每层 `begin/end` 缩进 4 空格；
- **一行一条语句**，复杂表达式适当换行；
- **位宽写清楚**，宁可啰嗦不要隐式扩展（第 10、11 章）；
- **表达式拿不准优先级就加括号**（第 10 章）。

### 2.4 可综合性与可移植性

- **不使用 `#` 延时做逻辑**（第 19 章）；
- **不用 `initial` 代替复位**（第 19 章）；
- **时钟只走全局时钟资源，衍生时钟尽量改成使能脉冲**（第 15、18 章）；
- **跨时钟域先同步**；
- **复位策略统一**（全同步或全异步+同步释放），不要混着来。

## 3. 读代码 checklist（重复即重点）

读一段 Verilog 时，按顺序问自己：

```text
[ ] 1. 这个 module 对应什么硬件？
[ ] 2. 每个端口的方向、类型、位宽是什么？
[ ] 3. 每条 assign 描述的是哪块组合逻辑？
[ ] 4. 每个 always 的敏感列表是 @(*) 还是 @(posedge clk)？
    - @(*)      -> 组合逻辑，用 = ，分支是否写全？
    - posedge   -> 时序逻辑，用 <= ，复位怎么处理？
[ ] 5. reg 到底综合成组合逻辑、锁存器还是触发器？
[ ] 6. 有没有多驱动、位宽截断、优先级陷阱？
[ ] 7. if/case 分支全不全？会不会出 latch？
[ ] 8. 多个 always / assign / 例化之间是并行关系，别按顺序理解。
```

## 4. 本章小结

> **组合用 `=`、时序用 `<=`，一个 always 只干一件事。**
> **组合分支不写全会出 latch；时序不写 else 是保持。**
> **assign 左值 wire，always 左值 reg；多驱动只允许三态。**
> **常量写位宽，表达式加括号，位宽算清楚。**
> **命名规范、缩进工整、注释写"为什么"。**
> **不用延时、不靠 initial 复位、时钟别乱分频。**

---

# 附录 A：章节内容来源与改动记录

## A.1 原笔记各章 → 新目录的映射

| 原笔记章节 | 新章节位置 | 处理方式 |
|---|---|---|
| 1. Verilog 开发目的 | 第 1 章 | 原样保留 |
| 2. 模块说明部分 | 第 2 章 | 保留，并合入"模块说明部分补充"（三天速成素材） |
| 3. assign 语句 | 第 5 章 | 保留，并合入"用数电理解 assign"（数电中的assign.md）与三天速成素材 |
| 4. 按位运算 | 第 6 章第一部分 | 保留 |
| 5. 移位运算 | 第 6 章第二部分 | 保留 |
| 5 尾部拼接引子 + 6. 拼接运算 | 第 6 章第三部分 | 合并（原文拼接引子原就接在移位章后） |
| 7. always 语句 | 第 7、8 章 | 拆分：always 主体 → 第 7 章；阻塞/非阻塞 → 第 8 章 |
| 8. 端口连接 | 第 12 章 | 保留（端口"声明"部分移到第 3 章） |
| 9. 门原语 | 第 14 章第 2、4 节 | 保留，归入常用组合电路 |
| 10. 数据类型 | 第 11 章第 1 节 | 保留 |
| 11. 数字的表示格式 | 第 11 章第 2 节 | 保留 |
| 12. if 语句 | 第 9 章第一部分 | 保留 |
| 13. case 语句 | 第 9 章第二部分 | 保留 |
| 14. 运算符总览与优先级 | 第 10 章 | 保留；其中按位/归约/移位/拼接小节加了"详见第 6 章"标记 |
| 15～20 章（原文只有标题） | 第 13～20 章 | 用知识库其他文件素材补全（见 A.2） |
| 原文散落的"端口列表""端口信号声明""模块定义"链接出现的章节 | 第 2、3 章 | 归位，链接全部保留 |

## A.2 补全章节及其素材来源

| 新章节 | 来源文件 |
|---|---|
| 第 2 章补充 | `01三天入门verilog速成.md`、`模块的定义.md`、`端口.md`、`端口信号三要素.md` |
| 第 3 章补充 | `端口信号三要素.md`、`端口.md`、`仿真时候不写端口列表的本质.md`、`wire和reg的对比.md` |
| 第 4 章 | `wire和reg的对比.md`、`01三天入门verilog速成.md`、`端口信号三要素.md` |
| 第 5 章补充 | `数电中的assign.md`、`01三天入门verilog速成.md` |
| 第 7 章补充 | `always语句.md` |
| 第 8 章补充 | `always语句.md` |
| 第 13 章 | `always语句.md`、`generate生成语句.md`、`02三天入门verilog速成.md` + Verilog-2001 通用语法 |
| 第 14 章 | `05A_三八译码器Verilog实现.md`、`数电中的assign.md` + 原文各组合电路例子 |
| 第 15 章 | `02三天入门verilog速成.md`、`01三天入门verilog速成.md` + 通用时序电路写法 |
| 第 16 章 | 原文第 9 章 FSM 例子 + `always语句.md`、`状态机.md` |
| 第 17 章 | `03B_仿真验证.md`、`端口.md`、`wire和reg的对比.md` |
| 第 18 章 | `03A_Verilog输入.md`、`03B_仿真验证.md`、`05A_三八译码器Verilog实现.md` + 约束通用知识 |
| 第 19 章 | 原文各章"不可综合"片段汇总 |
| 第 20 章 | 原文各章"常见错误"小节汇总 |

## A.3 保留的外部链接清单

本文档保留/新增的链接（均已验证目标文件存在）：

- [模块的定义.md](模块的定义.md)
- [端口.md](端口.md)
- [端口信号三要素.md](../FPGA设计竞赛/端口信号三要素.md)
- [仿真时候不写端口列表的本质.md](仿真时候不写端口列表的本质.md)
- [wire和reg的对比.md](wire和reg的对比.md)
- [数电中的assign.md](数电中的assign.md)
- [always语句.md](always语句.md)
- [位宽本质.md](位宽本质.md)
- [01三天入门verilog速成.md](../三天入门Verilog俗称/01三天入门verilog速成.md)
- [02三天入门verilog速成.md](../三天入门Verilog俗称/02三天入门verilog速成.md)
- [03A_Verilog输入.md](../小梅哥FPGA/03A_Verilog输入.md)
- [03B_仿真验证.md](../小梅哥FPGA/03B_仿真验证.md)
- [05A_三八译码器Verilog实现.md](../小梅哥FPGA/05A_三八译码器Verilog实现.md)

## A.4 标记说明

| 标记 | 含义 |
|---|---|
| `⭐【重点·重复】` | 该知识点在全篇出现两次以上，是初学重点/易错点 |
| `【不常用】` | 工程上很少用到的知识，了解即可 |
| `【补全·来源：xxx】` | 该段内容来自知识库其他文件，非原笔记正文 |
| `⚠️ 本章是补全章节` | 整章为补全，原笔记该章只有空标题 |
