/* static/js/edit_bin.js 
   ゴミ箱の編集フォームを表示し、フォームの送信を制御するスクリプト
*/

/* 選択された編集項目に応じて、対応する編集フォームを表示する関数
    value: 表示するフォームのタイプを示す文字列
        　 update_id, update_location, update_capacity, deleteのいずれか
*/
function showEditForm(value) {
    try {
        // すべてのフォームを非表示
        document.getElementById('id_edit_form').style.display = 'none';
        document.getElementById('location_edit_form').style.display = 'none';
        document.getElementById('capacity_edit_form').style.display = 'none';
        document.getElementById('delete_form').style.display = 'none';

        // 選択された編集項目に応じてフォームを表示
        if (value === 'update_id') {    // ID編集フォーム
            document.getElementById('id_edit_form').style.display = 'block';
            document.getElementById('new_bin_id').focus(); 
        } else if (value === 'update_location') {   // 設置場所編集フォーム
            document.getElementById('location_edit_form').style.display = 'block'; 
            document.getElementById('new_location').focus(); 
        } else if (value === 'update_capacity') {   // 容量編集フォーム
            document.getElementById('capacity_edit_form').style.display = 'block'; 
            document.getElementById('new_capacity').focus(); 
        } else if (value === 'delete') {    // ゴミ箱削除フォーム
            document.getElementById('delete_form').style.display = 'block'; 
        }
    } catch (error) {
        console.error('編集フォームの表示エラー: ', error); 
    }
}

/* フォームの送信を制御する関数 */
try {
    document.getElementById('edit-form').addEventListener('keydown', function(event) {
        if (event.key === 'Enter') { 
            event.preventDefault();     // デフォルトのフォーム送信を防ぐ
            const selectedEditOption = document.getElementById('edit_option').value; // 選択された編集オプションを取得

            try {
                // フォーム送信のための処理
                const form = document.getElementById('edit-form'); // フォーム要素を取得
                const input = document.createElement('input'); // input要素を作成
                input.type = 'hidden'; 

                // 選択された編集オプションに応じて、フォームのactionを設定して送信
                if (selectedEditOption === 'update_id' && document.getElementById('new_bin_id').value) {
                    input.name = 'action'; 
                    input.value = 'update_id'; // idの更新アクションを設定
                    form.appendChild(input); 
                    form.submit(); // フォームを送信
                } else if (selectedEditOption === 'update_location' && document.getElementById('new_location').value) {
                    input.name = 'action'; 
                    input.value = 'update_location'; // 設置場所の更新アクションを設定 
                    form.appendChild(input); 
                    form.submit(); // フォームを送信
                } else if (selectedEditOption === 'update_capacity' && document.getElementById('new_capacity').value) {
                    input.name = 'action'; 
                    input.value = 'update_capacity'; // 容量の更新アクションを設定 
                    form.appendChild(input); 
                    form.submit(); // フォームを送信
                } else if (selectedEditOption === 'delete') {
                    if (confirm('本当に削除しますか？')) { 
                        input.name = 'action'; 
                        input.value = 'delete'; // ゴミ箱の削除アクションを設定
                        form.appendChild(input); 
                        form.submit(); // フォームを送信
                    }
                }
            } catch (error) {
                console.error('フォーム送信中のエラー: ', error); 
            }
        }
    });
} catch (error) {
    console.error('イベントリスナーの設定中のエラー: ', error); 
}
