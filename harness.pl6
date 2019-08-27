use v6;

sub MAIN(*@pc-files, :$out-dir?) {
    my @failing-files;

    for @pc-files -> $pc-file {
        say "";
        
        if $out-dir {
            my $abc-file = IO::Path.new(basename => $pc-file.IO.basename,
                                        dirname => $out-dir).extension("abc");
            my $stdout-file = $abc-file.extension("stdout");
            my $stdout-handle = $stdout-file.open(:w);
            say "Trying $pc-file => $abc-file";
            run "python2.7", "pc2abc.py", $pc-file, $abc-file.Str, :out($stdout-handle);
            $stdout-handle.close;
        } else {
            my $abc-file = $pc-file.IO.extension: "abc";
            my $stdout-file = $abc-file.extension("stdout");
            my $stdout-handle = $stdout-file.open(:w);
            say "Trying $pc-file";
            run "python2.7", "pc2abc.py", $pc-file, :out($stdout-handle);
            $stdout-handle.close;
        }

        CATCH {
            default {
                @failing-files.push($pc-file);
            }
        }
    }

    dd @failing-files;
}