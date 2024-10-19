/* static/js/form.js 
    フォームに入力される値を制限するスクリプト
*/

document.addEventListener('DOMContentLoaded', function () {
    // ゴミ箱ID: 半角数字のみ、最大8文字
    const limitBinIdInput = function (inputElement) {
        const formatInput = function () {
            const inputValue = inputElement.value;

            // 半角数字のみ許可
            inputElement.value = inputValue.replace(/[^0-9]/g, '');

            // 最大8文字に制限
            if (inputElement.value.length > 8) {
                inputElement.value = inputElement.value.substring(0, 8);
            }
        };

        // 通常の入力イベントで制限をかける
        inputElement.addEventListener('input', formatInput);
        
        // IMEが終了したときにも制限をかける
        inputElement.addEventListener('compositionend', formatInput);
    };

    // bin_id に対する制限
    const binIdInput = document.getElementById('bin_id');
    if (binIdInput) {
        limitBinIdInput(binIdInput);
    }

    // searched_bin_id に対する制限
    const searchedBinIdInput = document.getElementById('searched_bin_id');
    if (searchedBinIdInput) {
        limitBinIdInput(searchedBinIdInput);
    }

    // selected_bin_id に対する制限
    const selectedBinIdInput = document.getElementById('selected_bin_id');
    if (selectedBinIdInput) {
        limitBinIdInput(selectedBinIdInput);
    }

    // new_bin_id に対する制限
    const newBinIdInput = document.getElementById('new_bin_id');
    if (newBinIdInput) {
        limitBinIdInput(newBinIdInput);
    }

    // 位置: 全角50文字まで
    const limitLocationInput = function (inputElement) {
        inputElement.addEventListener('input', function () {
            const locationInput = this;
            const location = locationInput.value;
            let length = 0;
            let maxLength = 50; // 全角50文字の制限
            let result = '';

            for (let i = 0; i < location.length; i++) {
                const char = location[i];
                // 全角文字は length+2, 半角文字は length+1 としてカウント
                if (char.match(/[^\x00-\xFF]/)) {
                    length += 2; // 全角は2文字分としてカウント
                } else {
                    length += 1; // 半角は1文字分としてカウント
                }

                // 制限を超えたらそれ以上の入力を無視
                if (length > maxLength * 2) {
                    break;
                }

                result += char;
            }

            // 入力値を制限後の結果に置き換える
            locationInput.value = result;
        });
    };

    // location に対する制限
    const locationInput = document.getElementById('location');
    if (locationInput) {
        limitLocationInput(locationInput);
    }

    // new_location に対する制限
    const newLocationInput = document.getElementById('new_location');
    if (newLocationInput) {
        limitLocationInput(newLocationInput);
    }
});
