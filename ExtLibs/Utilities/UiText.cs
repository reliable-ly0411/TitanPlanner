using System;
using System.Globalization;
using System.Collections.Concurrent;
using System.Security.Cryptography;
using System.Text;
using System.Resources;

namespace MissionPlanner.Utilities
{
    /// <summary>仅翻译显示文本；参数名、协议值和数值格式保持原样。</summary>
    public static class UiText
    {
        private static readonly ResourceManager Resources = new ResourceManager(
            "MissionPlanner.Utilities.Resources.UiText", typeof(UiText).Assembly);

        private static readonly ConcurrentDictionary<string, string> Keys = new ConcurrentDictionary<string, string>();

        private static string ResourceKey(string english)
        {
            // RESX 的键名判重不区分大小写；哈希保留源文大小写和换行的区别。
            using (var hash = SHA256.Create())
                return BitConverter.ToString(hash.ComputeHash(Encoding.UTF8.GetBytes(english)))
                    .Replace("-", "").ToLowerInvariant();
        }

        public static string Translate(string english)
        {
            // 每次读取当前 UI 语言，避免切换语言后仍命中旧语言缓存。
            return Resources.GetString(Keys.GetOrAdd(english, ResourceKey), CultureInfo.CurrentUICulture) ?? english;
        }

        public static string Format(FormattableString text)
        {
            // 只翻译格式模板；变量值和格式说明符由 .NET 原样处理。
            return string.Format(CultureInfo.CurrentCulture, Translate(text.Format), text.GetArguments());
        }
    }
}
