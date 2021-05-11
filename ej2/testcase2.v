module top(dat_r, dat_w, we, clk, rst, adr);
  input [3:0] adr;
  input clk;
  output [7:0] dat_r;
  reg [7:0] dat_r;
  input [7:0] dat_w;
  reg [3:0] mem_r_addr;
  wire [7:0] mem_r_data;
  reg [3:0] mem_w_addr;
  reg [7:0] mem_w_data;
  reg mem_w_en;
  input rst;
  input we;
  reg [7:0] mem [15:0];
  initial begin
    mem[0] = 8'h90;
    mem[1] = 8'hb3;
    mem[2] = 8'h23;
    mem[3] = 8'hfe;
    mem[4] = 8'ha7;
    mem[5] = 8'h4f;
    mem[6] = 8'h2c;
    mem[7] = 8'h5d;
    mem[8] = 8'h57;
    mem[9] = 8'h93;
    mem[10] = 8'h5a;
    mem[11] = 8'h77;
    mem[12] = 8'h51;
    mem[13] = 8'h12;
    mem[14] = 8'h6e;
    mem[15] = 8'h98;
  end
  reg [3:0] _0_;
  always @(posedge clk) begin
    _0_ <= mem_r_addr;
    if (mem_w_en) mem[mem_w_addr] <= mem_w_data;
  end
  assign mem_r_data = mem[_0_];
  always @* begin
    mem_r_addr = 4'h0;
    mem_r_addr = adr;
  end
  always @* begin
    dat_r = 8'h00;
    dat_r = mem_r_data;
  end
  always @* begin
    mem_w_addr = 4'h0;
    mem_w_addr = adr;
  end
  always @* begin
    mem_w_data = 8'h00;
    mem_w_data = dat_w;
  end
  always @* begin
    mem_w_en = 1'h0;
    mem_w_en = we;
  end
  reg [15:0] mem [15:0];
  initial begin
    mem[0] = 16'h90ae;
    mem[1] = 16'hb34c;
    mem[2] = 16'h237f;
    mem[3] = 16'hfe9d;
    mem[4] = 16'ha738;
    mem[5] = 16'h4f12;
    mem[6] = 16'h2c2a;
    mem[7] = 16'h5de5;
    mem[8] = 16'h57b3;
    mem[9] = 16'h938e;
    mem[10] = 16'h5a2a;
    mem[11] = 16'h774f;
    mem[12] = 16'h5187;
    mem[13] = 16'h1234;
    mem[14] = 16'h6ebc;
    mem[15] = 16'hfd98;
  end
endmodule
