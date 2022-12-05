module wrapper(
	   RST_N,

	   write_address,
	   write_data,
	   write_en,
	   write_rdy,

	   read_address,
	   read_en,
	   read_data,
	   read_rdy);


      reg  CLK;
      input  RST_N;
      
      // action method write
      input  [2 : 0] write_address;
      input  write_data;
      input  write_en;
      output write_rdy;
      
      // actionvalue method read
      input  [2 : 0] read_address;
      input  read_en;
      output read_data;
      output read_rdy;
      
      // signals for module outputs
      reg read_data;
      wire read_rdy, write_rdy;

      dut dut1(CLK,
	   RST_N,

	   write_address,
	   write_data,
	   write_en,
	   write_rdy,

	   read_address,
	   read_en,
	   read_data,
	   read_rdy);

    initial begin
        CLK = 0;
        forever begin
            #5 CLK = !CLK;
        end
    end

    initial begin
        $dumpfile("dump.vcd");
        $dumpvars;
    end

endmodule