package pers.jiangyinzuo.cabbagesearchwebsite.controller;

import org.apache.lucene.queryparser.classic.ParseException;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import pers.jiangyinzuo.cabbagesearchwebsite.DocsVO;
import pers.jiangyinzuo.cabbagesearchwebsite.LuceneHelper;

import java.io.IOException;

/**
 * @author Jiang Yinzuo
 */
@RestController
public class QueryController {

    @GetMapping("query")
    public DocsVO query(@RequestParam("lang") String lang, @RequestParam("q") String q) throws ParseException, IOException {
        return switch (lang) {
            case "en" -> LuceneHelper.searchEnglish(q, 10);
            case "cn" -> LuceneHelper.searchChinese(q, 10);
            default -> new DocsVO();
        };
    }
}
