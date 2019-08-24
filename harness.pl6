use v6;

sub MAIN(*@pc-files, :$out-dir?) {
    for @pc-files -> $pc-file {
        say "";
        
        if $out-dir {
            my $abc-file = IO::Path.new(basename => $pc-file.IO.basename,
                                        dirname => $out-dir).extension("abc");
            say "Trying $pc-file => $abc-file";
            run "python2.7", "pc2abc.py", $pc-file, $abc-file.Str;
        } else {
            say "Trying $pc-file";
            run "python2.7", "pc2abc.py", $pc-file;
            my $abc-file = $pc-file.IO.extension: "abc";
            # run "abc2ly", $abc-file.Str;
        }
    }
}