using System;
using System.Net;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace MissionPlannerTests
{
    [TestClass]
    public class TestEnvironment
    {
        [AssemblyInitialize]
        public static void Initialize(TestContext context)
        {
            // .NET Framework does not consume HTTPS_PROXY automatically.
            // Scope the explicitly supplied test proxy to this test process.
            var proxy = Environment.GetEnvironmentVariable("HTTPS_PROXY");
            if (!string.IsNullOrWhiteSpace(proxy))
                WebRequest.DefaultWebProxy = new WebProxy(new Uri(proxy), true);
        }
    }
}
