module mojo_top_0(
    // 50MHz clock input
    input clk,
    // Input from reset button (active low)
    input rst_n,
    // cclk input from AVR, high when AVR is ready
    input cclk,
    // Outputs to the 8 onboard LEDs
    output[7:0]led,
    // AVR SPI connections
    output spi_miso,
    input spi_ss,
    input spi_mosi,
    input spi_sck,
    // AVR ADC channel select
    output [3:0] spi_channel,
    // Serial connections
    input avr_tx, // AVR Tx => FPGA Rx
    output avr_rx, // AVR Rx => FPGA Tx
    input avr_rx_busy, // AVR Rx buffer full
    output slow_clk,
    input pdm_data
    );

wire rst = ~rst_n; // make reset active high
//wire int_slow_clk = slow_clk;

// these signals should be high-z when not used
assign spi_miso = 1'bz;
assign avr_rx = 1'bz;
assign spi_channel = 4'bzzzz;

assign led = 8'b0;

wire [7:0] tx_data;
wire new_tx_data;
wire tx_busy;
wire [7:0] rx_data;
wire new_rx_data;
 
clk_div_1 clk_div (
  .clk(clk),
  .reset(rst),
  .clk_out(slow_clk)
);

avr_interface_2 avr_interface (
  .clk(clk),
  .rst(rst),
  .cclk(cclk),
  .spi_miso(spi_miso),
  .spi_mosi(spi_mosi),
  .spi_sck(spi_sck),
  .spi_ss(spi_ss),
  .spi_channel(spi_channel),
  .tx(avr_rx), // FPGA tx goes to AVR rx
  .rx(avr_tx), 
  .channel(4'd15), // invalid channel disables the ADC
  .new_sample(),
  .sample(),
  .sample_channel(),
  .tx_data(tx_data),
  .new_tx_data(new_tx_data),
  .tx_busy(tx_busy),
  .tx_block(avr_rx_busy),
  .rx_data(rx_data),
  .new_rx_data(new_rx_data)
);

//message_printer zeroOnePrinter (
//  .clk(slow_clk),
//  .rst(rst),
//  .tx_data(tx_data),
//  .new_tx_data(new_tx_data),
//  .tx_busy(tx_busy),
//  .rx_data(rx_data),
//  .new_rx_data(new_rx_data),
//  .pdm_signal(pdm_data)
//);

helloPrinter_3 helloPrinter (
  .clk(clk),
  .rst(rst),
  .tx_data(tx_data),
  .new_tx_data(new_tx_data),
  .tx_busy(tx_busy),
  .rx_data(rx_data),
  .new_rx_data(new_rx_data)
);
endmodule