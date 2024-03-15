using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace ConsoleApp1
{
    internal class Program
    {
        static async Task Main(string[] args)
        {
            Console.Write("Enter Email: ");
            string email = Console.ReadLine();
            Console.Write("Enter Password: ");
            string password = Console.ReadLine();
            await getToken(email, password);

        }
        async static Task getToken(string email, string pass)
        {
            string url = "https://discord.com/api/v9/auth/login";
            var payload = new Dictionary<string, string>()
            {
                {"login", email }, { "password", pass}
            };
            string JsonPayLoad = JsonConvert.SerializeObject(payload);
            HttpClient client = new HttpClient();
            StringContent stringContent = new StringContent(JsonPayLoad, Encoding.UTF8, "application/json");
            HttpResponseMessage response = await client.PostAsync(url, stringContent);
            if (response.IsSuccessStatusCode)
            {
                Console.WriteLine("\nLogin Successful!");
                string responseContent = await response.Content.ReadAsStringAsync();
                Console.WriteLine(responseContent);
                JObject json = JObject.Parse(responseContent);
                Console.WriteLine($"User ID: {json["user_id"]}");
                Console.WriteLine($"User ID: {json["token"]}");
                Console.ReadKey();
            }
            else
            {
                Console.WriteLine(response.ReasonPhrase);
            }
         }
        
    }
}