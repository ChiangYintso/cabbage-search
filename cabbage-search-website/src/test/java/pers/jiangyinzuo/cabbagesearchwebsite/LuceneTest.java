package pers.jiangyinzuo.cabbagesearchwebsite;

import org.apache.lucene.queryparser.classic.ParseException;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

import java.io.IOException;

class LuceneTest {
    @Test
    void searchTest() {
        try {
            var docVO = LuceneHelper.searchEnglish("Wall Street", 2);
            Assertions.assertEquals(2, docVO.filePath().size());
            Assertions.assertTrue(docVO.timeSpent() > 0);
        } catch (ParseException | IOException e) {
            e.printStackTrace();
        }
    }

}
