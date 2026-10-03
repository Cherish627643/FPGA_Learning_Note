# Verilog always 语句（电赛/FPGA竞赛重点）

> 适配：Sipeed Tang（高云Gowin），Verilog-2001，竞赛考点，区分**组合逻辑 / 时序逻辑**，这是FPGA最容易踩坑的语法。

## 一、基础概念

`always` 是**过程块语句**，块内可以写顺序语句（`if/else`、`case`），**不是C语言的while循环！**

> 硬件本质：描述一段硬件电路，上电后持续响应敏感事件，不是软件循环。

语法模板：

```Verilog
always @(敏感列表) begin
    // 顺序语句
end
```

> `@()`：敏感事件，当括号内信号变化，才执行一次块内代码。

---

## 二、两大使用场景【竞赛必考】

### 1. 时序逻辑（触发器，寄存器）

**敏感列表：时钟 + 复位**

```Verilog
// 同步复位（推荐，Gowin FPGA资源更优）
always @(posedge clk) begin
    if(rst_n == 1'b0) begin
        q <= 1'b0;
    end else begin
        q <= d;
    end
end
```

```Verilog
// 异步复位（电赛常用，复位立刻生效）
always @(posedge clk or negedge rst_n) begin
    if(!rst_n) begin
        q <= 1'b0;
    end else begin
        q <= d;
    end
end
```

✅ 规则：

- 时序逻辑用**非阻塞赋值 `<=`**
- `posedge`：上升沿；`negedge`：下降沿
- 异步复位：复位信号要放进敏感列表

### 2. 组合逻辑（纯组合电路，无寄存器）

**敏感列表：所有输入信号**
>**敏感列表（`@(*)` 除外）写的是：在这个 `always` 块内部被读取 / 用到的信号，不是整个模块的全部输入！** `@(*)` 就是自动收集【本 always 块内读取的所有信号】，不需要手动写。
```Verilog
always @(*) begin // @(*) 自动敏感列表（Verilog2001，竞赛首选！）
    if(a) begin
        y = b;
    end else begin
        y = c;
    end
end
```

✅ 规则：

- 组合逻辑用**阻塞赋值 `=`**
- 必须覆盖所有分支，**防止生成锁存器（latch）！电赛高频扣分点**
- 禁止写`posedge clk`（组合逻辑没有时钟）

> ❌ 坑：`always @(a,b)` 手动写敏感列表，容易漏写信号，推荐统一用 `@(*)`

---

## 三、阻塞赋值 `=` vs 非阻塞赋值 `<=`【重中之重】

|类型|赋值符号|使用场景|硬件行为|
|---|---|---|---|
|阻塞赋值|`=`|**组合逻辑 always @(*)**|立即生效，顺序执行，阻塞后面语句|
|非阻塞赋值|`<=`|**时序逻辑 always @(posedge clk)**|块结束后统一更新，并行，模拟寄存器|

> 一句话口诀：**时序用<=，组合用=，千万别混用！**

错误示例（竞赛常错）：

```verilog
always @(posedge clk) begin
    a = b; // ❌ 时序块内使用阻塞赋值，仿真与综合不一致
end
```

---

## 四、敏感列表详解

1. `@(*)`：自动敏感，块内所有读取的信号自动加入敏感列表，**组合逻辑首选**
2. `posedge clk`：时钟上升沿触发
3. `negedge clk`：时钟下降沿触发
4. `posedge clk or negedge rst_n`：时钟上升沿 或 复位下降沿 → **异步复位**

> 不要写 `always` 不带敏感列表：`always begin ... end`，会造成无限循环仿真，综合报错。

---

## 五、always 内支持语句

在`always`的`begin-end`块内部，可以写：

1. `if-else` 分支
2. `case / casez / casex`（状态机核心！）
3. `for` 循环（可综合，生成重复硬件）
4. 任务task调用
    
    > ❌ 不能直接在always块里例化模块，模块例化必须写在always外面
    

### case示例（状态机，电赛高频）

```verilog
reg [1:0] curr_state;
always @(posedge clk or negedge rst_n) begin
    if(!rst_n) begin
        curr_state <= 2'd0;
    end else begin
        case(curr_state)
            2'd0: curr_state <= 2'd1;
            2'd1: curr_state <= 2'd2;
            2'd2: curr_state <= 2'd0;
            default: curr_state <= 2'd0; // default防止锁存
        endcase
    end
end
```

---

## 六、综合禁忌（电赛踩坑清单）

1. **组合逻辑分支不全 → 生成latch锁存器！** 组合逻辑`if`必须有`else`；`case`必须写`default`
2. 同一个信号，**不能在多个always块里同时赋值**（多驱动，编译报错）
3. 不要在时序always块写组合逻辑赋值混用
4. `@(*)` 只用于组合逻辑，不要加时钟沿

---

## 七、补充：三种always的写法速记

```
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

---

## 八、课后小练习（电赛风格）

1. 写一段always，实现：上升沿clk，异步低复位，寄存器输出q = d
2. 写组合逻辑always @(*)，y = a&b | c；
3. 找出下面代码错误：

```
always @(posedge clk) begin
    if(en)
        out = in;
end
```

如果你需要，我把这一节**整合进之前那份Verilog竞赛MD文档**，或者单独输出一份 `always语句.md`。你想要哪个？