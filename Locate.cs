// This code is for Educational only
// Note use Microsoft Visual Studio
// Console App (.NETframework)
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Task;
using System.Net.Http;
// this will get error but go into your project side and right click.
// find Manage NuGet Packages and download first name Newtonsoft.Json.
using Newtonsoft.Json;

namespace locate{

    public class Data{
        public string city {get; set;}
        public string region {get; set;}
        public string country {get; set;}
        public string loc {get; set;}
        public string org {get; set;}
        public string postal {get; set;}
        public string timezone {get; set;}

    }

    internal class program{

        static async Task Main(string[]args){

            Console.Title = "Locate";
            Console.Write = "Enter IP Adress: ";
            string ip = Console.ReadLine();
            string url = $"https://ipInfo.io/{ip}/json";

            using (HttpCient cient = new HttpCient()){
                
                try{
                    HttpResponse response = await cient.GetAsync(url);
                    response.EnsureSuccessStatusCode();

                Console.WriteLine("[+] Request Successfully Made");
                string responseData = await response.Content.ReadAsStringAsync();

                Data ipInfo = JsonConvert.DeserializObject<Data>(responseData);
                Console.Clear();
                Console.WriteLine($"Country: {ipInfo.country}");
                Console.WriteLine($"City: {ipInfo.city}");
                Console.WriteLine($"Coordinates: {ipInfo.loc}");
                Console.WriteLine($"Postal Code: {ipInfo.postal}");
                Console.WriteLine($"Region: {ipInfo.region}");
                Console.WriteLine($"ASN: {ipInfo.org}");
                string[] coords = ipInfo.loc.Split(',');
                Console.WriteLine($"Google Maps: https://www.google.com/maps/?q={Coords[0]},{Coords[1]}")
                }

                catch (HttpRequestException ex){
                    Console.WriteLine($"Error: {ex.Message}");
                }
            }
        }
    }
}