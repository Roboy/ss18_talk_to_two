module hello_world_rom (
    input clk,
    input [5:0] addr,
    output [7:0] data
  );
 
  wire [7:0] rom_data [17:0];
 
  assign rom_data[0] = " ";
  assign rom_data[1] = "H";
  assign rom_data[2] = "e";
  assign rom_data[3] = "l";
  assign rom_data[4] = "l";
  assign rom_data[5] = "o";
  assign rom_data[6] = " ";
  assign rom_data[7] = "\n";
  assign rom_data[8] = "\r";
  assign rom_data[9] = " ";
  assign rom_data[10] = "W";
  assign rom_data[11] = "o";
  assign rom_data[12] = "r";
  assign rom_data[13] = "l";
  assign rom_data[14] = "d";
  assign rom_data[15] = "!";
  assign rom_data[16] = "\n";
  assign rom_data[17] = "\r";
 
  reg [7:0] data_d, data_q;
 
  assign data = data_q;
 
  always @(*) begin
    if (addr > 5'd17)
      data_d = " ";
    else
      data_d = rom_data[addr];
  end
 
  always @(posedge clk) begin
    data_q <= data_d;
  end
 
endmodule