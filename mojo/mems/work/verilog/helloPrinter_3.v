module helloPrinter_3 (
    input clk,
    input rst,
    output [7:0] tx_data,
    output reg new_tx_data,
    input tx_busy,
    input [7:0] rx_data,
    input new_rx_data
  );
 
  localparam STATE_SIZE = 2;
  localparam IDLE = 0,
    PRINT_MESSAGE = 1,
    PRINT_HELLO = 2,
    PRINT_WORLD = 3;
    
 
  localparam MESSAGE_LEN = 14; // real length(if array to 13 it is a 14)
  localparam HELLO_LEN = 9;
  localparam WORLD_LEN = 9;
 
  reg [STATE_SIZE-1:0] state_d, state_q;
 
  reg [5:0] addr_d, addr_q;
 
  hello_world_rom_8 message_rom (
  .clk(clk),
  .addr(addr_q),
  .data(tx_data)
  );
 
  always @(*) begin
    state_d = state_q; // default values
    addr_d = addr_q;   // needed to prevent latches
    new_tx_data = 1'b0;
 
    case (state_q)
      IDLE: begin
        if (new_rx_data && rx_data == "h") begin
          state_d = PRINT_HELLO;
          addr_d = 5'd0;
        end
        if (new_rx_data && rx_data == "w") begin
          state_d = PRINT_WORLD;
          addr_d = 5'd9;
        end
        else 
          addr_d = 5'd0;
      end
      PRINT_MESSAGE: begin
        if (!tx_busy) begin
          new_tx_data = 1'b1;
          addr_d = addr_q + 1'b1;
          if (addr_q == MESSAGE_LEN-1)
            state_d = IDLE;
        end
      end
      PRINT_HELLO: begin
        if (!tx_busy) begin
          new_tx_data = 1'b1;
          addr_d = addr_q + 1'b1;
          if (addr_q == HELLO_LEN-1)
            state_d = IDLE;
        end
      end
      PRINT_WORLD: begin
        if (!tx_busy) begin
          new_tx_data = 1'b1;
          addr_d = addr_q + 1'b1;
          if (addr_q == WORLD_LEN-1+HELLO_LEN)
            state_d = IDLE;
        end
      end
      default: state_d = IDLE;
    endcase
  end
 
  always @(posedge clk) begin
    if (rst) begin
      state_q <= IDLE;
    end else begin
      state_q <= state_d;
    end
 
    addr_q <= addr_d;
  end
 
endmodule