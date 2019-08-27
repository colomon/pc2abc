use v6;

my @failing-files;

sub convert-pc-file($pc-file, :$out-dir?) {
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

sub MAIN(*@pc-files, :$out-dir?) {
    for @pc-files -> $pc-file {
        given $pc-file {
            when .IO.d {
                for $pc-file.IO.dir(test => { $_ ~~ /:i ".pc" $ / }) -> $file {
                    convert-pc-file($file, :$out-dir);
                }
            }
            default {
                convert-pc-file($pc-file, :$out-dir);
            }
        }
    }

    dd @failing-files;
}