// Ethical Exploration - IP Geolocation & ASN Lookup Tool
// License: GNU General Public License v3.0 (GPL-3.0)
// Requirements: Newtonsoft.Json NuGet Package (.NET Framework / .NET Core / .NET 6+)

using System;
using System.Net.Http;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace EthicalExploration.Recon
{
    public class IpData
    {
        [JsonProperty("ip")]
        public string Ip { get; set; }

        [JsonProperty("city")]
        public string City { get; set; }

        [JsonProperty("region")]
        public string Region { get; set; }

        [JsonProperty("country")]
        public string Country { get; set; }

        [JsonProperty("loc")]
        public string Loc { get; set; }

        [JsonProperty("org")]
        public string Org { get; set; }

        [JsonProperty("postal")]
        public string Postal { get; set; }

        [JsonProperty("timezone")]
        public string Timezone { get; set; }
    }

    internal class LocateProgram
    {
        private static readonly HttpClient HttpClient = new HttpClient();

        static async Task Main(string[] args)
        {
            Console.Title = "Ethical Exploration - IP Geolocation Tool";
            Console.WriteLine("=================================================");
            Console.WriteLine("    Ethical Exploration - IP Recon & Geolocation ");
            Console.WriteLine("=================================================");

            string ip = string.Empty;
            if (args != null && args.Length > 0 && !string.IsNullOrWhiteSpace(args[0]))
            {
                ip = args[0].Trim();
            }
            else
            {
                Console.Write("Enter IP Address (leave blank for local external IP): ");
                ip = Console.ReadLine()?.Trim() ?? string.Empty;
            }

            string url = string.IsNullOrWhiteSpace(ip) 
                ? "https://ipinfo.io/json" 
                : $"https://ipinfo.io/{Uri.EscapeDataString(ip)}/json";

            try
            {
                Console.WriteLine($"\n[*] Querying Geolocation Intelligence for: {(string.IsNullOrEmpty(ip) ? "Current IP" : ip)}...");
                
                HttpClient.DefaultRequestHeaders.UserAgent.ParseAdd("EthicalExploration-Recon/1.0");
                HttpResponseMessage response = await HttpClient.GetAsync(url);
                response.EnsureSuccessStatusCode();

                string responseData = await response.Content.ReadAsStringAsync();
                IpData ipInfo = JsonConvert.DeserializeObject<IpData>(responseData);

                if (ipInfo != null)
                {
                    Console.WriteLine("\n[+] GEOLOCATION INTELLIGENCE REPORT:");
                    Console.WriteLine("-------------------------------------------------");
                    Console.WriteLine($" IP Address    : {ipInfo.Ip ?? ip}");
                    Console.WriteLine($" Country       : {ipInfo.Country ?? "N/A"}");
                    Console.WriteLine($" Region/State  : {ipInfo.Region ?? "N/A"}");
                    Console.WriteLine($" City          : {ipInfo.City ?? "N/A"}");
                    Console.WriteLine($" Postal Code   : {ipInfo.Postal ?? "N/A"}");
                    Console.WriteLine($" Timezone      : {ipInfo.Timezone ?? "N/A"}");
                    Console.WriteLine($" ASN / Org     : {ipInfo.Org ?? "N/A"}");
                    Console.WriteLine($" Coordinates   : {ipInfo.Loc ?? "N/A"}");

                    if (!string.IsNullOrEmpty(ipInfo.Loc) && ipInfo.Loc.Contains(","))
                    {
                        string[] coords = ipInfo.Loc.Split(',');
                        if (coords.Length == 2)
                        {
                            Console.WriteLine($" Maps Link     : https://www.google.com/maps/?q={coords[0].Trim()},{coords[1].Trim()}");
                        }
                    }
                    Console.WriteLine("-------------------------------------------------");
                }
                else
                {
                    Console.WriteLine("[-] Error: Failed to deserialize geolocation response.");
                }
            }
            catch (HttpRequestException ex)
            {
                Console.WriteLine($"[!] Network Request Error: {ex.Message}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[!] Unexpected Error: {ex.Message}");
            }

            Console.WriteLine("\nScan complete. Press any key to exit...");
        }
    }
}
