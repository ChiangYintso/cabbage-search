package pers.jiangyinzuo.cabbagesearchwebsite;

import java.util.Objects;
import java.util.Set;

public record DocsVO(
        Set<DocVO> filePath,
        long timeSpent
) {
    static record DocVO(
            String title,
            Integer docId
    ) {
        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            DocVO docVO = (DocVO) o;
            return docId.equals(docVO.docId);
        }

        @Override
        public int hashCode() {
            return Objects.hash(docId);
        }
    }

    public DocsVO() {
        this(Set.of(), 0);
    }


}
