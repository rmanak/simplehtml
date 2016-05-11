#!/usr/bin/perl

sub file_to_text {
	$fname=$_[0];
	my $txt;
	$txt='';
	if ( !open INPUTDATA, $fname ) {
		die "cannot open $fname: $!";
	}
	while (<INPUTDATA>) {
		$txt = $txt . $_;
	}
	return $txt;
}

$num_args=$#ARGV +1;
if ($num_args != 4) {
	die "\n  Usage: xxx file\n\n";
}

#post hyper code:
$phc="JDHALOWPFHSNC";

#date hyper code:
$dhc="ASDLKJFHG";

#sidebar hyper code:
$shc="KJDSADPFP";

#footbar hyper code:
$fhc="KDLPQHFZVD";

$template_file=$ARGV[0];
$side_file=$ARGV[1];
$foot_file=$ARGV[2];
$post_file=$ARGV[3];

$txtsuffix = '.txt';
$post_filetmp = `basename -s .w $post_file`;
chomp $post_filetmp;
$post_filet =  $post_filetmp . $txtsuffix;

$TEMPTXT=&file_to_text($template_file);
$POSTTXT=&file_to_text($post_file);
$SIDETXT=&file_to_text($side_file);
$FOOTBARTXT=&file_to_text($foot_file);

#creating date:
# fix for unix using mydate.py
#$lstupddaynum=`date +%d -r $post_filet`;
#chomp $lstupddaynum;
#$lstupddayw=`date +%a -r $post_filet`;
#chomp $lstupddayw;
#$lstupdyear=`date +%Y -r $post_filet`;
#chomp $lstupdyear;
#$lstupdmon=`date +%b -r $post_filet`;
#chomp $lstupdmon;

#$date="$lstupddayw $lstupdmon $lstupddaynum, $lstupdyear";

$date = `./bin/mydate.py $post_filet`;
chomp $date;

$title='';
if ($POSTTXT =~ /(title\s*:=\s*{\s*)([^}]*?)(\s*})/s) {
   $title=$2;
	$POSTTXT =~ s/title\s*:=\s*{[^}]*}//sg;
} else {
	if ($POSTTXT =~ /(<h1>\s*)([^:]*)(:*)(\s*<\/h1>)/s ) {
		$title = $2;
	}
}

$author='';
if ($POSTTXT =~ /(author\s*:=\s*{\s*)([^}]*?)(\s*})/s) {
	$author=$2;
	$POSTTXT =~ s/author\s*:=\s*{[^}]*}//sg;
}


$keywords='';
if ($POSTTXT =~ /(keywords\s*:=\s*{\s*)([^}]*?)(\s*})/s) {
	$keywords=$2;
	$POSTTXT =~ s/keywords\s*:=\s*{[^}]*}//sg;
}

$description='';
if ($POSTTXT =~ /(description\s*:=\s*{\s*)([^}]*?)(\s*})/s) {
	$description=$2;
	$POSTTXT =~ s/description\s*:=\s*{[^}]*}//sg;
}

if ($title ne ''){
  $TEMPTXT=~ s/<title>.*<\/title>/<title>$title<\/title>/sg;
}

$tl='"';

if ($keywords ne '') {
 $TEMPTXT =~ s/(<meta name=${tl}keywords${tl} content=$tl)([^$tl]*)($tl\s*\/>)/$1$keywords$3/sg;
}

if ($author ne '') {
 $TEMPTXT =~ s/(<meta name=${tl}author${tl} content=$tl)([^$tl]*)($tl\s*\/>)/$1$author$3/sg;
}


if ($description ne '') {
 $TEMPTXT =~ s/(<meta name=${tl}description${tl} content=$tl)([^$tl]*)($tl\s*\/>)/$1$description$3/sg;
}

$dl_syn='\[dl\]';
$dl_op='<img src="img/dl.svg" />';

$ext_lnk_syn='\[>\]';
$ext_lnk_op='<img style="margin-left:1px;" src="img/external-link.svg" alt="" align="bottom" />';

$toc_syn='\[TOC\]';
$toc_op='<div class="table_of_contents"></div>';

# Creating references:

$num_ref=0;
$ref_text='';
$is_there_ref=0;
$reftbl{"HDQIFZMXCNAPQEDJALFX"}=0;
while ($POSTTXT =~ /(%%\s*)(\w+.*?)(\s*%%)/ ) {
  $is_there_ref=1;
  $lnk_nm =$2;
  if ( ! exists $ref_nums{$lnk_nm} ) {
	$num_ref++;
	$ref_nums{$lnk_nm}=$num_ref;
	$POSTTXT =~ s/(%%\s*)$lnk_nm(\s*%%)/<sup><a href="#ref$lnk_nm" id="cnt$lnk_nm">\[$num_ref\]<\/a><\/sup>/;
	if ($POSTTXT =~ /(\{\s*$lnk_nm\s*:\s*)([^\}]*)(\})/s ) {
		$each_ref = '<a href="#cnt'.$lnk_nm.'" id="ref'.$lnk_nm.'">[' . $num_ref . ']</a>: '. $2;
		$ref_txt = $ref_txt . '<p>' .  $each_ref . '</p>' . "\n";
	   $POSTTXT =~ s/(\{\s*$lnk_nm\s*:\s*)([^\}]*)(\})//sg; 
	} 
  } else{
	  $num = $ref_nums{$lnk_nm};
	  $POSTTXT =~ s/(%%\s*)$lnk_nm(\s*%%)/<sup><a href="#ref$lnk_nm" id="cnt$lnk_nm">\[$num\]<\/a><\/sup>/;
  }
}

if ($is_there_ref==1) {
$POSTTXT = $POSTTXT . '<hr />' . '<h2>References</h2>' . $ref_txt;
}


$TEMPTXT=~ s/$dhc/$date/sg;
$TEMPTXT=~ s/$phc/$POSTTXT/sg;
$TEMPTXT=~ s/$shc/$SIDETXT/sg;
$TEMPTXT=~ s/$fhc/$FOOTBARTXT/sg;
$TEMPTXT=~ s/$ext_lnk_syn/$ext_lnk_op/sg;
$TEMPTXT=~ s/$dl_syn/$dl_op/sg;
$TEMPTXT=~ s/$toc_syn/$toc_op/sg;

$img_op1='<div style="max-width:350px; width:auto; padding:2px; height:auto; text-align:justify; border: solid #BBBBBB 1px;float:right; margin-left:8px;"><img style="display:block; height:auto; width:auto; max-width:320px; margin-left:auto; margin-right:auto;" src="';
$img_op2='" alt="';
$img_op3='" border="0" /><hr />';
$img_op3noline='" border="0" />';
$img_op4='</div>';
$TEMPTXT=~ s/({{}}\(\()(.*?)(\)\))/$img_op1$2$img_op2$img_op3noline$img_op4/sg;
$TEMPTXT=~ s/({{)(.*?)(}}\(\()(.*?)(\)\))/$img_op1$4$img_op2$img_op3$2$img_op4/sg;


$imgc_op1='<div style="margin-left:auto; margin-right:auto; padding:3px; text-align:justify; border:solid #BBBBBB 1px; height:auto; width: auto; max-width:500px;"><img style="display:block; height:auto; width:auto; max-width:470px; margin-left:auto; margin-right:auto;" src="';
$imgc_op2='" alt="';
$imgc_op3='" border="0" /><hr />';
$imgc_op3noline='" border="0" />';
$imgc_op4='</div>';
$TEMPTXT=~ s/({{}}\[\[)(.*?)(\]\])/$imgc_op1$2$imgc_op2$imgc_op3noline$imgc_op4/sg;
$TEMPTXT=~ s/({{)(.*?)(}}\[\[)(.*?)(\]\])/$imgc_op1$4$imgc_op2$imgc_op3$2$imgc_op4/sg;

$r_op1='<div style="max-width:350px; width:auto; padding:2px; height:auto; text-align:justify; border: solid #BBBBBB 1px;float:right; margin-left:8px;">';
$r_op2='</div>';

$TEMPTXT =~ s/(<R>)(.*?)(<\/R>)/$r_op1$2$r_op2/sg;

print $TEMPTXT;
