#!/usr/bin/perl


#full language support for code2html
#ada, ada95, awk, c, c++, cc, cpp, cxx, gpasm, groff, html, java, javascript, js, lisp, m4, make, makefile, pas, pascal, patch, perl, plain, pov, povray, python, ruby, sh, shellscript, sql

#language support we are using:
sub what_lang{
	my $lang;
	$lang = $_[0];
	my $ret =
	  ($lang='C') ? 'c' :
	  ($lang='CPP') ? 'cpp':
	  ($lang='PERL') ? 'perl':
	  ($lang='HTL') ? 'html':
	  ($lang='AWK') ? 'awk':
	  ($lang='JAVA') ? 'java':
	  ($lang='PYTHON') ? 'python':
	  ($lang='SH') ? 'sh':
	  ($lang='SQL') ? 'sql':
	  ($lang='ADA') ? 'ADA':
	  ($lang='JAVASCRIPT') ? 'JAVASCRIPT':
	  ($lang='JS') ? 'JS':
	  ($lang='MAKE') ? 'make':
	  ($lang='PASCAL') ? 'pascal':
	  ($lang='RUBY') ? 'ruby':
	  ($lang='LISP') ? 'lisp':
	                   'undefined';
}

sub code_match {
	my $string;
	$string = $_[0];
	$lang = $_[1];
	if ( $string =~ /(<$lang>)(.*?)(<\/$lang>)/s ) { return 1;}
	else {return 0;}
}

sub code_replace {
	my $string;
	my $tld;
	$tld = "'";
	$string = $_[0];
	$stringb = $_[0];
	$stringa = $_[0];
	$lang = $_[1];
	if ($string =~ /(.*)(<$lang>\s*)(.*?)(\s*<\/$lang>)(.*)/s ) {
		$before = $1;
		$code = $3;
		chomp($code);
		$after = $5;
	}
	open TMP, " > tmp_code_123" or die "cannot pipe to file:$!";
	print TMP $code;
	close TMP;
	$l2 = &what_lang($lang);
	`./bin/code2html -l $tld$l2$tld 2>/dev/null tmp_code_123 > tmp_code_1234`;
	$code = `cat tmp_code_1234`;

	$code =~ s/(.*)(<pre>\s*)(.*?)(\s*<\/pre>)(.*)/$2$3$4/sg;
	chomp($code);
   
	return $before . $code . $after;
}


$tmp='';
while ( <> ) {
	$tmp = $tmp . $_;
}

@all_langs = qw( C CPP PERL HTL AWK SQL SH PYTHON JAVA );

foreach $lang (@all_langs) {
  $count = 0;
  while( &code_match($tmp,$lang) ) {
	  $tmp=&code_replace($tmp,$lang);
	  $count=$count + 1;
	  if ($count > 1000) {die "something went wrong!"}
  }
  
}

print $tmp;


