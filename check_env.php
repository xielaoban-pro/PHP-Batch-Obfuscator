<?php
header("Content-Type: text/html; charset=utf-8");

echo "<h2>声达网络加密环境检测 (sdczz.com)</h2>";
echo "<hr>";

$errors = [];

// 1. 检测 PHP 版本
echo "<strong>1. PHP 版本: </strong> " . phpversion();
if (version_compare(phpversion(), '5.3.0', '<')) {
    echo " <span style='color:red'>[警告] 版本过低，无法运行 Goto 混淆模式</span><br>";
} else {
    echo " <span style='color:green'>[通过]</span><br>";
}

// 2. 检测 zlib 扩展
echo "<strong>2. Zlib 扩展 (解压支持): </strong> ";
if (extension_loaded('zlib')) {
    echo "<span style='color:green'>[通过]</span><br>";
} else {
    $errors[] = "Zlib 扩展未加载，无法运行 Gzip/Xor/Ultra 模式";
    echo "<span style='color:red'>[失败] Zlib 未加载</span><br>";
}

// 3. 检测 eval 函数 (核心)
echo "<strong>3. eval() 函数 (核心执行): </strong> ";
$disabled_functions = explode(',', ini_get('disable_functions'));
$is_disabled = false;
foreach ($disabled_functions as $func) {
    if (trim($func) == 'eval') {
        $is_disabled = true;
        break;
    }
}

// 另外检测 Suhosin 等安全补丁是否禁用了 eval
if ($is_disabled) {
    $errors[] = "eval() 函数被禁用 (php.ini disable_functions)";
    echo "<span style='color:red'>[失败] 被禁用</span><br>";
} else {
    // 尝试实际运行一下
    $test = 'return true;';
    try {
        if (@eval($test) === true) {
            echo "<span style='color:green'>[通过]</span><br>";
        } else {
            // 有些环境虽然没在 disable_functions 里，但通过其他方式禁用了
            $errors[] = "eval() 函数无法正常执行，可能被安全插件拦截";
            echo "<span style='color:red'>[失败] 执行被拦截</span><br>";
        }
    } catch (Exception $e) {
        $errors[] = "eval() 执行出错: " . $e->getMessage();
        echo "<span style='color:red'>[失败]</span><br>";
    }
}

echo "<hr>";
if (count($errors) > 0) {
    echo "<h3 style='color:red'>检测结果: 环境不支持!</h3>";
    echo "<ul>";
    foreach ($errors as $err) {
        echo "<li>$err</li>";
    }
    echo "</ul>";
} else {
    echo "<h3 style='color:green'>检测结果: 环境完美支持!</h3>";
    echo "您可以放心运行所有模式的加密文件。";
}
?>