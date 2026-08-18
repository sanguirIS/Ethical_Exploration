// Ethical Exploration - Discord API Authentication & Token Utility
// License: GNU General Public License v3.0 (GPL-3.0)
// Requirements: Newtonsoft.Json NuGet Package (.NET 6+ / .NET Framework)

using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace EthicalExploration.DiscordAuth
{
    internal class Program
    {
        private static readonly HttpClient HttpClient = new HttpClient();

        static async Task Main(string[] args)
        {
            Console.Title = "Ethical Exploration - Discord Token Authentication Utility";
            Console.WriteLine("=================================================");
            Console.WriteLine("   Ethical Exploration - Discord Auth Utility    ");
            Console.WriteLine("=================================================");

            string email = string.Empty;
            string password = string.Empty;

            if (args != null && args.Length >= 2)
            {
                email = args[0];
                password = args[1];
            }
            else
            {
                Console.Write("Enter Email: ");
                email = Console.ReadLine()?.Trim() ?? string.Empty;

                Console.Write("Enter Password: ");
                password = ReadMaskedPassword();
            }

            if (string.IsNullOrEmpty(email) || string.IsNullOrEmpty(password))
            {
                Console.WriteLine("\n[!] Error: Email and password cannot be empty.");
                return;
            }

            await GetTokenAsync(email, password);
        }

        private static string ReadMaskedPassword()
        {
            StringBuilder sb = new StringBuilder();
            while (true)
            {
                ConsoleKeyInfo key = Console.ReadKey(true);
                if (key.Key == ConsoleKey.Enter)
                {
                    Console.WriteLine();
                    break;
                }
                else if (key.Key == ConsoleKey.Backspace)
                {
                    if (sb.Length > 0)
                    {
                        sb.Remove(sb.Length - 1, 1);
                        Console.Write("\b \b");
                    }
                }
                else if (!char.IsControl(key.KeyChar))
                {
                    sb.Append(key.KeyChar);
                    Console.Write("*");
                }
            }
            return sb.ToString();
        }

        private static async Task GetTokenAsync(string email, string pass)
        {
            string url = "https://discord.com/api/v9/auth/login";
            var payload = new Dictionary<string, string>()
            {
                { "login", email },
                { "password", pass },
                { "undelete", "false" }
            };

            string jsonPayload = JsonConvert.SerializeObject(payload);
            using (var request = new HttpRequestMessage(HttpMethod.Post, url))
            {
                request.Headers.Add("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36");
                request.Content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");

                try
                {
                    Console.WriteLine("\n[*] Authenticating against Discord API endpoint...");
                    HttpResponseMessage response = await HttpClient.SendAsync(request);
                    string responseContent = await response.Content.ReadAsStringAsync();

                    if (response.IsSuccessStatusCode)
                    {
                        Console.WriteLine("\n[+] Authentication Successful!");
                        JObject json = JObject.Parse(responseContent);

                        string userId = json["user_id"]?.ToString() ?? "N/A";
                        string token = json["token"]?.ToString() ?? "N/A";

                        Console.WriteLine("-------------------------------------------------");
                        Console.WriteLine($" User ID : {userId}");
                        Console.WriteLine($" Token   : {token}");
                        Console.WriteLine("-------------------------------------------------");
                    }
                    else
                    {
                        Console.WriteLine($"\n[-] Authentication Failed: HTTP {(int)response.StatusCode} {response.ReasonPhrase}");
                        try
                        {
                            JObject errorJson = JObject.Parse(responseContent);
                            if (errorJson["message"] != null)
                            {
                                Console.WriteLine($"[-] Reason: {errorJson["message"]}");
                            }
                            if (errorJson["captcha_key"] != null)
                            {
                                Console.WriteLine("[!] CAPTCHA verification required for this account/IP.");
                            }
                            if (errorJson["mfa"] != null && (bool)errorJson["mfa"])
                            {
                                Console.WriteLine("[*] Multi-Factor Authentication (MFA/2FA) is enabled on this account.");
                                Console.WriteLine($"[*] Ticket: {errorJson["ticket"]}");
                            }
                        }
                        catch
                        {
                            Console.WriteLine($"[-] Response: {responseContent}");
                        }
                    }
                }
                catch (HttpRequestException ex)
                {
                    Console.WriteLine($"[!] Network Connection Error: {ex.Message}");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[!] Error: {ex.Message}");
                }
            }
        }
    }
}
