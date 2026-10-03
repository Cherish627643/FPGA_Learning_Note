# Verilog HDL 新手学习文档（适配 Sipeed Tang / Gowin 高云，竞赛向）

> 适用：Sipeed Tang 系列FPGA（Gowin高云），电赛/嵌入式芯片竞赛入门 包含：可综合主代码 + Testbench仿真代码；语法基础 → 模块例化 → 状态机 → FIFO → 时序约束入门；附带常见坑点 目标：新手从零上手，能独立写简单工程，看懂竞赛常用模块

---

## 目录

 [[#1. Verilog 基础概念]]
 [[#2. 数据类型]]
 [[#3. 运算符]]
[[#4. 模块基础 module / endmodule]]
[[#5. 连续赋值 assign（组合逻辑）]]
[[#6. 过程块 always（组合+时序逻辑）]]
[[#7. 模块例化（竞赛高频）]]
[[#8. 阻塞赋值 vs 非阻塞赋值【重中之重】]]
[[#9. 有限状态机 FSM（竞赛必考）]]
[[#10. FIFO 原理与 Gowin IP调用]]
[[#12. 时序约束入门（Gowin）]]
[[#13. 竞赛高频踩坑清单]]
[[#14. 课后练习]]

---

## 1. Verilog 基础概念

Verilog 不是C语言！**硬件描述语言，描述电路硬件并行执行**，不是顺序执行软件。

- `module`：硬件模块，相当于一个硬件芯片
- 所有`assign`、`always`块**并行同时运行**，不是从上到下依次执行
- 分为两类代码：
    1. **可综合代码**：可以编译、布局布线，烧写到FPGA硬件（写在顶层/功能模块）
    2. **仿真代码(Testbench)**：仅用于仿真，**不可综合**，用来给输入激励、观测输出

> Gowin IDE（Sipeed Tang使用）：语法标准 Verilog-2001，支持大部分常用语法

---

## 2. 数据类型

### 2.1 可综合（硬件电路使用）

|类型|说明|使用场景|
|---|---|---|
|`wire`|线网，导线，只能由连续赋值`assign`驱动|组合逻辑连线，模块端口|
|`reg`|寄存器，存储单元，在`always`块内赋值|时序逻辑触发器；组合逻辑always@(*)内也可用reg|

> ⚠️ reg ≠ FPGA里的触发器！只有在**时钟沿触发always块**里，综合后才会生成触发器；`always@(*)`里的reg只会生成组合逻辑

### 2.2 仿真专用（不可综合，仅Testbench）

- `integer`：整型变量，循环计数
- `time`：时间类型
- `initial`：仿真启动时执行，硬件不存在，只能写在testbench中

### 2.3 位宽定义语法

```Verilog
wire [7:0] data_w;   // 8位wire，bit7~bit0
reg  [15:0] cnt_r;   // 16位reg
wire [0:3]  dat;     // 高位在后，不推荐，竞赛统一用 [MSB:LSB]
```

常量写法：

```Verilog
4'd5     // 4位十进制5
4'b0101  // 4位二进制
4'h5     // 4位十六进制
```

`x`：未知；`z`：高阻态。

---

## 3. 运算符

竞赛常用优先级：括号 > 一元 > 乘除 > 加减 > 移位 > 比较 > 逻辑与 > 逻辑异或 > 逻辑或 > 三目

```Verilog
// 算术：+ - * / %
// 位运算：&(按位与) |(按位或) ^(异或) ~(按位取反)
// 逻辑运算：&& || ! （返回1bit 0/1，用于判断）
// 移位：<< >>
// 拼接 { } 【超级常用】    {A2,A1,A0}
{1'b0, data}              // 高位补0
{cnt[7:4], cnt[3:0]}      // 高低4位交换

// 三目运算符，组合逻辑首选
assign y = en ? a : b;
```

> ❗坑：`&` 和 `&&` 不要混用！`&`是按位运算，`&&`是逻辑判断

---

## 4. 模块基础 module / endmodule

模块 = 一个硬件单元，包含[端口](端口.md)定义 + 内部逻辑。

```Verilog
// 模块模板，可综合
module led_blink(
    input  wire clk,      // 输入时钟
    input  wire rst_n,    // 复位，低电平复位（竞赛推荐低复位）
    output reg  led       // 输出，在always内赋值所以用reg
);

// 内部逻辑写这里

endmodule
```

端口方向：`input` / `output` / `inout`双向口（慎用，竞赛尽量避开inout）

---

## 5. 连续赋值 assign（组合逻辑）

`assign`：并行赋值，**组合逻辑，无寄存器**。 适用：简单与或、多路选择、连线。

```Verilog
wire a, b, y;
assign y = a & b;

// 多路选择
assign out = sel ? in1 : in0;
```

⚠️ 规则：**同一个wire只能被一处assign驱动，否则出现多驱动冲突，编译报错**

---

## 6. 过程块 always（组合+时序逻辑）

### 6.1 组合逻辑 always@(*)

`@(*)` 敏感列表自动包含所有右侧输入信号，纯组合逻辑，无触发器。

```Verilog
reg y;
always @(*) begin
    if(a)
        y = b;
    else
        y = c;
end
```

> 组合逻辑必须**所有分支都给y赋值**，否则生成锁存器latch！竞赛大忌

### 6.2 时序逻辑 always@(posedge clk)

时钟沿触发，会综合出触发器寄存器，最常用。

```Verilog
reg [25:0] cnt;
always @(posedge clk or negedge rst_n) begin // 低电平复位，复位放敏感列表
    if(!rst_n) begin
        cnt <= 26'd0;
    end else begin
        cnt <= cnt + 1'b1;
    end
end
```

> 写法规范：时序逻辑**用非阻塞 <=**

---

## 7. 模块例化（竞赛高频）

模块化设计：顶层调用子模块，工程大了必须用。

两种写法：位置映射（不推荐，容易错），**命名映射（竞赛推荐）**

子模块：`div_clk`分频模块

```Verilog
module div_clk(
    input  wire clk_in,
    input  wire rst_n,
    output reg  clk_out
);
// 分频逻辑省略
endmodule
```

顶层例化：

```Verilog
module top(
    input  clk,
    input  rst_n,
    output led
);

wire clk_1hz;

// 命名关联 .子模块端口(顶层信号)
div_clk u_div_clk(
    .clk_in  (clk),
    .rst_n   (rst_n),
    .clk_out (clk_1hz)
);

endmodule
```

`u_div_clk`：例化名，自定义，多个例化名不能重复。

---

## 8. 阻塞赋值 vs 非阻塞赋值【重中之重】

竞赛最容易踩分坑，务必牢记！

### 8.1 阻塞赋值 `=`

- 顺序执行，立即生效
- 使用场景：`always@(*)` 组合逻辑
- ❌ 不要在时钟always时序块使用

### 8.2 非阻塞赋值 `<=`

- 赋值更新在时钟沿结束后，并行更新
- 使用场景：`always@(posedge clk)` 时序逻辑（寄存器）
- ❌ 不要在组合always@(*)内使用

> 口诀：**组合用=，时序用<=；assign只能用=**

---

## 9. 有限状态机 FSM（竞赛必考）

竞赛常用三段式状态机，可读性好、易综合、便于时序优化。

- 一段式：简单，不推荐复杂工程
- 二段式：状态寄存器 + 组合输出，容易产生组合逻辑毛刺
- ✅ **三段式**：【竞赛首选】
    1. 时序逻辑：状态跳转寄存器
    2. 组合逻辑：状态跳转判断
    3. 时序/组合：输出逻辑（推荐时序输出消毛刺）

```Verilog
// 三段式FSM模板
module fsm_demo(
    input  wire clk,
    input  wire rst_n,
    input  wire start,
    output reg  done
);

// 定义状态
localparam IDLE   = 2'b00;
localparam WORK   = 2'b01;
localparam FINISH = 2'b10;

reg [1:0] curr_state;
reg [1:0] next_state;

// 第一段：时序逻辑，更新当前状态
always @(posedge clk or negedge rst_n) begin
    if(!rst_n)
        curr_state <= IDLE;
    else
        curr_state <= next_state;
end

// 第二段：组合逻辑，判断下一状态
always @(*) begin
    next_state = curr_state; // 默认保持，避免锁存
    case(curr_state)
        IDLE: begin
            if(start)
                next_state = WORK;
            else
                next_state = IDLE;
        end
        WORK: begin
            next_state = FINISH;
        end
        FINISH: begin
            next_state = IDLE;
        end
        default: next_state = IDLE;
    endcase
end

// 第三段：时序输出，消除毛刺
always @(posedge clk or negedge rst_n) begin
    if(!rst_n)
        done <= 1'b0;
    else begin
        case(curr_state)
            FINISH: done <= 1'b1;
            default: done <= 1'b0;
        endcase
    end
end

endmodule
```

> 要点：`localparam` 定义状态常量（优于`define`）；case写default防止锁存；时序输出消除毛刺

---

## 10. FIFO 原理与 Gowin IP调用

竞赛数据跨时钟域、高速缓存必备。

### 10.1 FIFO基础概念

- 写端口：wr_clk, wr_en, din, full
- 读端口：rd_clk, rd_en, dout, empty
- **同步FIFO**：读写同一个时钟
- **异步FIFO**：读写不同时钟（跨时钟域，竞赛高频）

> Sipeed Tang(Gowin) 直接调用Gowin官方FIFO IP核，**不建议手写异步FIFO**（亚稳态极易出错）

### 10.2 Gowin IP调用简要步骤

1. Gowin IDE → IP Core Generator
2. 搜索FIFO，选择FIFO IP
3. 配置：位宽、深度、同步/异步、full/empty信号
4. 生成IP，在顶层模块例化，和普通模块用法一致

> 注意：异步FIFO必须做格雷码跨时钟域同步，手写极易踩坑，竞赛优先用IP

---

## 11. Testbench 仿真写法

tb模块**无端口**，只能仿真，不能综合到硬件。 关键字：`initial`、`#`延时，`$display`打印，`$stop`停止仿真。

```Verilog
`timescale 1ns / 1ns  // 时间单位 / 时间精度

module tb_fsm_demo;

// 信号声明
reg  clk;
reg  rst_n;
reg  start;
wire done;

// 例化待测试模块
fsm_demo u_fsm(
    .clk   (clk),
    .rst_n (rst_n),
    .start (start),
    .done  (done)
);

// 时钟生成 50MHz 周期20ns
initial begin
    clk = 1'b0;
    forever #10 clk = ~clk;
end

// 激励信号
initial begin
    rst_n = 1'b0;
    start = 1'b0;
    #20;
    rst_n = 1'b1;
    #30;
    start = 1'b1;
    #20;
    start = 1'b0;
    #200;
    $stop;
end

endmodule
```

> `forever`无限循环生成时钟，tb专属；仿真工具：Gowin内置Simulator / Modelsim

---

## 12. 时序约束入门（Gowin）

竞赛时序问题：建立时间、保持时间，高频时序报错最常见。 约束文件后缀 `.sdc`，在Gowin工程中添加。

### 12.1 核心约束

**1. 时钟约束 create_clock（最重要！）**

告诉工具主时钟频率，工具才会做时序分析。

```
# 50MHz时钟，周期20ns
create_clock -name clk -period 20 [get_ports clk]
```

**2. 输入延迟 set_input_delay**

**3. 输出延迟 set_output_delay**

**4. 伪路径 set_false_path**：跨时钟域路径，不需要检查时序（异步FIFO读写时钟之间加）

> 竞赛经验：低速工程（<50M）不写约束可能能跑；一旦时钟100M+、高速数据传输，**必须加sdc约束**，否则时序违例，硬件不稳定

---

## 13. 竞赛高频踩坑清单

1. 组合逻辑`always@(*)`分支不全 → latch锁存器，时序恶化
2. 时序块误用`=`，组合块误用`<=` → 仿真和硬件行为不一致
3. 多驱动：同一个信号多处assign/always赋值 → 编译报错
4. 复位问题：敏感列表忘记写复位信号，高低复位混用
5. 跨时钟域：直接把信号从clkA传到clkB，不做两级打拍同步 → 亚稳态，随机出错
6. FIFO：full/empty判断时机错误，写满继续写，读空继续读
7. 状态机缺少default分支，生成锁存器
8. Testbench代码复制到主模块：initial不可综合，烧录报错
9. 位宽不匹配：`cnt <= cnt + 1`，忘记扩展位，溢出

---

## 14. 课后练习

适配Tang开发板，循序渐进。

1. **练习1**：写LED分频闪烁模块，50MHz系统时钟，生成1Hz；写对应的Testbench仿真
2. **练习2**：模块例化，顶层调用分频模块，控制LED
3. **练习3**：三段式状态机，按键触发，依次点亮3个LED，完成后拉高done
4. **练习4**：调用Gowin同步FIFO IP，写顶层例化+tb，测试写满、读空逻辑

---

> 本文档为Verilog竞赛入门语法，基于Gowin/Sipeed Tang平台 后续进阶：跨时钟域处理（两级寄存器打拍）、PLL IP、RAM、UART、SPI，时序分析报告查看

---

### 使用说明

1. 全选复制以上全部内容
2. 新建文本文档，粘贴内容
3. 文件 → 另存为 → 编码选择 **UTF-8**，文件名：`verilog_fpga_gowin.md`
4. 可用 Typora / Obsidian / VSCode / 任何Markdown阅读器打开

需要我再补充一份**配套4道练习题的完整源码（可直接导入Gowin工程）**吗？