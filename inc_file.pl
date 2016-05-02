#!/usr/bin/perl

#full language support for code2html
#ada, ada95, awk, c, c++, cc, cpp, cxx, gpasm, groff, html, java, javascript, js, lisp, m4, make, makefile, pas, pascal, patch, perl, plain, pov, povray, python, ruby, sh, shellscript, sql

#language support we are using:
sub file_match {
	my $string;
	$string = $_[0];
	if ( $string =~ /(<FILE=")(.*?)(">)/s ) { 
		return 1;
	}
	else {return 0;}
}

sub file_to_text {
	$fname=$_[0];
	my $txt;
	$txt='';
	if ( !open INPUTDATA, $fname ) {
		warn "cannot open $fname: $!";
	} else {
	   while (<INPUTDATA>) {
		  $txt = $txt . $_;
   	}
   }
	return $txt;
}


sub file_replace {
	my $string;
	$string = $_[0];
	if ($string =~ /(.*)(<FILE=")(.*?)(">)(.*)/s ) {
		$before = $1;
		$fname = $3;
		$after = $5;
	}
	
	$file_content=&file_to_text($fname);
   
	return $before . $file_content . $after;
}


$tmp='';
while ( <> ) {
	$tmp = $tmp . $_;
}

  $count = 0;
  while( &file_match($tmp) ) {
	  $tmp=&file_replace($tmp);
	  $count=$count + 1;
	  if ($count > 1000) {die "something went wrong!"}
  }
  
print $tmp;


