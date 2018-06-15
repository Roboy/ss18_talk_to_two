module message_rom (
    input clk,
    input [3:0] addr,
    output [7:0] data
  );
 
  wire [7:0] rom_data [13:0];
 
  assign rom_data[0] = "H";
  assign rom_data[1] = "e";
  assign rom_data[2] = "l";
  assign rom_data[3] = "l";
  assign rom_data[4] = "o";
  assign rom_data[5] = " ";
  assign rom_data[6] = "W";
  assign rom_data[7] = "o";
  assign rom_data[8] = "r";
  assign rom_data[9] = "l";
  assign rom_data[10] = "d";
  assign rom_data[11] = "!";
  assign rom_data[12] = "\n";
  assign rom_data[13] = "\r";
 
  reg [7:0] data_d, data_q;
 
  assign data = data_q;
 
  always @(*) begin
    if (addr > 4'd13)
      data_d = " ";
    else
      data_d = rom_data[addr];
  end
 
  always @(posedge clk) begin
    data_q <= data_d;
  end
 
endmodule