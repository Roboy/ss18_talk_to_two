module message_rom (
    input clk,
    input [4:0] addr,
    output [7:0] data
  );
 
  wire [7:0] rom_data [11:0];
 
  //assign rom_data[0] = " ";
  //assign rom_data[1] = "H";
  //assign rom_data[2] = "e";
  //assign rom_data[3] = "l";
  //assign rom_data[4] = "l";
  //assign rom_data[5] = "o";
  //assign rom_data[6] = " ";
  //assign rom_data[7] = "\n";
  //assign rom_data[8] = "\r";
  //assign rom_data[9] = " ";
  //assign rom_data[10] = "W";
  //assign rom_data[11] = "o";
  //assign rom_data[12] = "r";
  //assign rom_data[13] = "l";
  //assign rom_data[14] = "d";
  //assign rom_data[15] = "!";
  //assign rom_data[16] = "\n";
  //assign rom_data[17] = "\r";
  
  assign rom_data[0] = " ";
  assign rom_data[1] = "0";
  assign rom_data[2] = "\n";
  assign rom_data[3] = "\r";
  assign rom_data[4] = " ";
  assign rom_data[5] = "1";
  assign rom_data[6] = "\n";
  assign rom_data[7] = "\r";
  assign rom_data[8] = " ";
  assign rom_data[9] = "X";
  assign rom_data[10] = "\n";
  assign rom_data[11] = "\r";
 
  reg [7:0] data_d, data_q;
 
  assign data = data_q;
 
  always @(*) begin
    if (addr > 4'd11)
      data_d = " ";
    else
      data_d = rom_data[addr];
  end
 
  always @(negedge clk) begin
    data_q <= data_d;
  end
 
endmodule