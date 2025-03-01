from scraper import HoujinBangouScraper
import argparse


def parse_args():
    """コマンドライン引数をパースする"""
    parser = argparse.ArgumentParser(description='法人番号検索システム')
    parser.add_argument(
        '--company',
        type=str,
        help='検索する会社名'
    )
    parser.add_argument(
        '--prefecture',
        type=str,
        help='都道府県名'
    )
    parser.add_argument(
        '--city',
        type=str,
        help='市区町村名'
    )
    parser.add_argument(
        '--details',
        type=str,
        help='丁目番地等の詳細住所'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='search_results.csv',
        help='出力ファイル名（デフォルト: search_results.csv）'
    )
    parser.add_argument(
        '--show-browser',
        action='store_true',
        help='ブラウザを表示する（デフォルト: 非表示）'
    )
    return parser.parse_args()


def main():
    """メイン実行関数"""
    # コマンドライン引数の取得
    args = parse_args()
    
    if not args.company and not (args.prefecture and args.city):
        print('エラー: 会社名、または都道府県と市区町村を指定してください。')
        return
    
    try:
        # スクレイパーの初期化と実行
        scraper = HoujinBangouScraper(headless=not args.show_browser)
        results = scraper.search_company(
            company_name=args.company,
            prefecture=args.prefecture,
            city=args.city,
            details=args.details
        )
        
        if results is not None and not results.empty:
            # 結果の表示
            print('\n検索結果:')
            print(results)
            
            # CSVファイルとして保存
            results.to_csv(
                args.output,
                index=False,
                encoding='utf-8-sig'
            )
            print(f'\n結果を {args.output} に保存しました。')
        else:
            print('検索結果が見つかりませんでした。')
            
    except Exception as e:
        print(f'エラーが発生しました: {str(e)}')


if __name__ == '__main__':
    main()