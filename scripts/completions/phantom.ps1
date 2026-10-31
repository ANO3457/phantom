# PowerShell completion for phantom.
#
# Install by dot-sourcing this file in your PowerShell profile ($PROFILE):
#   . <path-to-phantom>/scripts/completions/phantom.ps1
#
# A new shell session will then complete subcommands, flags, and values:
#   phantom <TAB>         -> check, inspect, run, generate, diff, verify
#   phantom check --<TAB> -> --strict, --format, --deny, --allow-only
#   phantom run --<TAB>   -> --timeout, --deny, --allow-only, ...

Register-ArgumentCompleter -Native -CommandName phantom -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)

    $subcommands = @('check', 'inspect', 'run', 'generate', 'diff', 'verify')
    $elements = $commandAst.Elements | Select-Object -ExpandProperty Value

    $subcommand = $null
    for ($i = 1; $i -lt $elements.Count; $i++) {
        if ($elements[$i] -in $subcommands) {
            $subcommand = $elements[$i]
            break
        }
    }

    $prev = if ($elements.Count -ge 2) { $elements[-1] } else { '' }

    # Values for flags that take a fixed set of values
    if ($prev -eq '--format') {
        @('text', 'sarif') | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
        }
        return
    }

    if ($prev -eq '--encoding') {
        @('comment', 'whitespace', 'unicode') | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
        }
        return
    }

    # Before a subcommand: offer subcommands or global flags
    if (-not $subcommand) {
        if ($wordToComplete -like '-*') {
            @('-h', '--help', '--version', '-V', '--no-color') | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
                [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterName', $_)
            }
        } else {
            $subcommands | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
                [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
            }
        }
        return
    }

    # After a subcommand: offer only that subcommand's flags
    $flags = switch ($subcommand) {
        'check' {
            @('-h', '--help', '--strict', '--format', '--deny', '--allow-only')
        }
        'inspect' {
            @('-h', '--help', '--json', '--strict', '--deny', '--allow-only')
        }
        'run' {
            @('-h', '--help', '--timeout', '--deny', '--allow-only', '--handlers-from', '--allow-handler')
        }
        'generate' {
            @('-h', '--help', '--stdin', '--intent', '--placement', '--encoding', '--output', '-o', '--dry-run', '--provider', '--plan-file', '--allow-remote')
        }
        'diff' {
            @('-h', '--help', '--host-only', '--no-color')
        }
        'verify' {
            @('-h', '--help', '--timeout')
        }
    }

    if ($wordToComplete -like '-*') {
        $flags | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterName', $_)
        }
    } else {
        Get-ChildItem -Path "$wordToComplete*" | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new($_.Name, $_.Name, 'ProviderItem', $_.FullName)
        }
    }
}
