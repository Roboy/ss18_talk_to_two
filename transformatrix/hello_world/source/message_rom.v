module message_rom (
    input clk,
    input [3:0] addr,
    output [7:0] data
  );
 
  wire [7:0] rom_data [15:0];
 
  assign rom_data[0] = "H";
  assign rom_data[1] = "e";
  assign rom_data[2] = "l";
  assign rom_data[3] = "l";
  assign rom_data[4] = "o";
  assign rom_data[5] = " ";
  assign rom_data[6] = "\n";
  assign rom_data[7] = "\r";
  assign rom_data[8] = "W";
  assign rom_data[9] = "o";
  assign rom_data[10] = "r";
  assign rom_data[11] = "l";
  assign rom_data[12] = "d";
  assign rom_data[13] = "!";
  assign rom_data[14] = "\n";
  assign rom_data[15] = "\r";
 
  reg [7:0] data_d, data_q;
 
  assign data = data_q;
 
  always @(*) begin
    if (addr > 4'd15)
      data_d = " ";
    else
      data_d = rom_data[addr];
  end
 
  always @(posedge clk) begin
    data_q <= data_d;
  end
 
endmodule