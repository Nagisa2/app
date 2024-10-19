/* static/js/menu.js
   メニューの表示/非表示を切り替えるためのスクリプト
*/

document.addEventListener('DOMContentLoaded', function () {
    // DOMが読み込まれた後の処理
    try {
        // メニューのトグルボタンとメニュー要素を取得
        const menuToggle = document.querySelector('.menu-toggle'); // メニューを表示/非表示にするボタン
        const menu = document.querySelector('.menu');  // メニュー要素

        // menuToggleまたはmenuが存在しない場合
        if (!menuToggle || !menu) {
            throw new Error('Menu toggleまたはmenuが存在しません。'); 
        }

        // メニューのトグルボタンにクリックイベントリスナーを追加
        menuToggle.addEventListener('click', function () {
            try {
                // メニューの表示/非表示を切替え
                menu.classList.toggle('active'); 
            } catch (error) {
                console.error('メニューの表示切り替えエラー: ', error); 
            }
        });
    } catch (error) {
        console.error('メニューの初期化エラー: ', error); 
    }
});
