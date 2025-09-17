while read -r sym; do
  ./export_stl.sh "$sym"
done < trivial-faces.dat 