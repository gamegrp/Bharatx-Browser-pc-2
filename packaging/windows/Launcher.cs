// SPDX-License-Identifier: MPL-2.0
using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Text;
using System.Windows.Forms;

[assembly: AssemblyTitle("BharatX Browser")]
[assembly: AssemblyProduct("BharatX Browser")]
[assembly: AssemblyCompany("Nitai Studio")]
[assembly: AssemblyCopyright("Copyright 2026 Nitai Studio")]
[assembly: AssemblyVersion("1.36.0.0")]
[assembly: AssemblyFileVersion("1.36.0.0")]

internal static class Launcher
{
    // Windows CommandLineToArgvW-compatible quoting, including trailing slashes.
    internal static string Quote(string value)
    {
        var result = new StringBuilder("\"");
        int slashes = 0;
        foreach (char character in value)
        {
            if (character == '\\') { slashes++; continue; }
            if (character == '"')
                result.Append('\\', slashes * 2 + 1).Append('"');
            else
                result.Append('\\', slashes).Append(character);
            slashes = 0;
        }
        return result.Append('\\', slashes * 2).Append('"').ToString();
    }

    [STAThread]
    private static int Main(string[] args)
    {
        try
        {
            string root = AppDomain.CurrentDomain.BaseDirectory;
            string ini = Path.Combine(root, "browser", "application.ini");
            string exe = Path.Combine(root, "BharatXCore.exe");
            if (!File.Exists(exe) || !File.Exists(ini))
                throw new FileNotFoundException("The browser installation is incomplete. Reinstall BharatX Browser from Microsoft Store.");
            var command = new StringBuilder("-app ").Append(Quote(ini));
            foreach (string arg in args) command.Append(' ').Append(Quote(arg));
            var start = new ProcessStartInfo(exe, command.ToString());
            start.WorkingDirectory = root;
            start.UseShellExecute = false;
            start.EnvironmentVariables["XUL_APP_FILE"] = ini;
            start.EnvironmentVariables["MOZ_CRASHREPORTER_DISABLE"] = "1";
            start.EnvironmentVariables["MOZ_TELEMETRY_REPORTING"] = "0";
            using (var process = Process.Start(start))
            {
                if (process == null) throw new InvalidOperationException("The browser could not be started.");
                // Keep the packaged application process alive for shell activation.
                process.WaitForExit();
                return process.ExitCode;
            }
        }
        catch (Exception error)
        {
            MessageBox.Show(error.Message + "\n\nSupport: nitai.grp00@gmail.com", "BharatX Browser", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
    }
}
