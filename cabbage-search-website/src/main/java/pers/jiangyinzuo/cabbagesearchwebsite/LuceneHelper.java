package pers.jiangyinzuo.cabbagesearchwebsite;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;

import java.io.*;
import java.nio.file.Paths;
import java.util.*;
import java.util.stream.Collectors;

/**
 * @author Jiang Yinzuo
 */
public class LuceneHelper {
    private static final String LUCENE_PREFIX_PATH = "build";
    private static final String LUCENE_EN_INDEX_PATH = LUCENE_PREFIX_PATH + "/lucene_en_index/";
    private static final String LUCENE_CN_INDEX_PATH = LUCENE_PREFIX_PATH + "/lucene_cn_index";

    private static final String LUCENE_CN_TITLE_FILE = LUCENE_PREFIX_PATH + "/gmw_titles.txt";
    private static final String LUCENE_EN_TITLE_FILE = LUCENE_PREFIX_PATH + "/china_daily_titles.txt";

    private static final String LUCENE_DOC_CN_PATH = LUCENE_PREFIX_PATH + "/gmw_article/";
    private static final String LUCENE_DOC_EN_PATH = LUCENE_PREFIX_PATH + "/china_daily_article/";

    private static final String ID_FIELD = "id";
    private static final String TITLE_FIELD = "title";
    private static final String CONTENT_FIELD = "content";
    private static final String FULL_PATH_FIELD = "fullPath";

    private static final IndexSearcher EN_SEARCHER = loadDocs(LUCENE_EN_INDEX_PATH, LUCENE_EN_TITLE_FILE, LUCENE_DOC_EN_PATH);
    private static final IndexSearcher CN_SEARCHER = loadDocs(LUCENE_CN_INDEX_PATH, LUCENE_CN_TITLE_FILE, LUCENE_DOC_CN_PATH);

    private static IndexSearcher loadDocs(String indexPath, String titleFile, String docPath) {
        try (Directory idxDir = FSDirectory.open(Paths.get(indexPath));
             BufferedReader titleReader = new BufferedReader(new FileReader(titleFile))) {
            File docEnDir = new File(docPath);
            File[] enDataFiles = docEnDir.listFiles();
            Analyzer analyzer = new StandardAnalyzer();
            var iwConfig = new IndexWriterConfig(analyzer);
            var idxWriter = new IndexWriter(idxDir, iwConfig);
            assert enDataFiles != null;

            int docId = 0;
            for (File cnDataFile : enDataFiles) {
                try (var reader = new FileReader(cnDataFile)) {
                    var doc = new Document();

                    doc.add(new TextField(ID_FIELD, Integer.toString(docId++), Field.Store.YES));
                    var title = titleReader.readLine();
                    doc.add(new TextField(TITLE_FIELD, title, Field.Store.YES));
                    doc.add(new TextField(CONTENT_FIELD, reader));
                    doc.add(new TextField(FULL_PATH_FIELD, cnDataFile.getCanonicalPath(), Field.Store.YES));
                    idxWriter.addDocument(doc);
                }

            }
            idxWriter.commit();
            idxWriter.close();
            IndexReader idxReader = DirectoryReader.open(idxDir);
            return new IndexSearcher(idxReader);
        } catch (IOException e) {
            e.printStackTrace();
        }
        return null;
    }

    private LuceneHelper() {
    }


    public static DocsVO searchEnglish(String q, int count) throws ParseException, IOException {
        return search(q, count, EN_SEARCHER);
    }

    public static DocsVO searchChinese(String q, int count) throws ParseException, IOException {
        return search(q, count, CN_SEARCHER);
    }

    private static DocsVO search(String q, int count, IndexSearcher searcher) throws ParseException, IOException {
        Analyzer analyzer = new StandardAnalyzer();
        var queryParser = new QueryParser(CONTENT_FIELD, analyzer);
        var query = queryParser.parse(q);
        long start = System.currentTimeMillis();

        var topDocs = searcher.search(query, count);

        long end = System.currentTimeMillis();
        Set<DocsVO.DocVO> contents = Arrays.stream(topDocs.scoreDocs).map(scoreDoc -> {
            DocsVO.DocVO docVO = null;
            try {
                var doc = searcher.doc(scoreDoc.doc);
                docVO = new DocsVO.DocVO(doc.get(TITLE_FIELD), Integer.parseInt(doc.get(ID_FIELD)));
            } catch (IOException e) {
                e.printStackTrace();
            }
            return docVO;
        }).collect(Collectors.toSet());

        return new DocsVO(contents, end - start);
    }
}
